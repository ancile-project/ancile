import torch
import requests
import json
from collections import defaultdict
import datetime
import torch.nn as nn
import time
import os
import math

def batchify(data, bsz):
    # Work out how cleanly we can divide the dataset into bsz parts.
    nbatch = data.size(0) // bsz
    # Trim off any extra elements that wouldn't cleanly fit (remainders).
    data = data.narrow(0, 0, nbatch * bsz)
    # Evenly divide the data across the bsz batches.
    data = data.view(bsz, -1).t().contiguous()
    return data


def repackage_hidden(h):
    """Wraps hidden states in new Tensors, to detach them from their history."""
    if isinstance(h, torch.Tensor):
        return h.detach()
    else:
        return tuple(repackage_hidden(v) for v in h)


# get_batch subdivides the source data into chunks of length args.bptt.
# If source is equal to the example output of the batchify function, with
# a bptt-limit of 2, we'd get the following two Variables for i = 0:
# ┌ a g m s ┐ ┌ b h n t ┐
# └ b h n t ┘ └ c i o u ┘
# Note that despite the name of the function, the subdivison of data is not
# done along the batch dimension (i.e. dimension 1), since that was handled
# by the batchify function. The chunks are along dimension 0, corresponding
# to the seq_len dimension in the LSTM.

def get_batch(source, i, bptt):
    seq_len = min(bptt, len(source) - 1 - i)
    data = source[i:i + seq_len]
    target = source[i + 1:i + 1 + seq_len].view(-1)
    return data, target


def evaluate(model, data_source, ntokens, eval_batch_size, bptt, criterion):
    # Turn on evaluation mode which disables dropout.
    model.eval()
    total_loss = 0.
    hidden = model.init_hidden(eval_batch_size)
    with torch.no_grad():
        for i in range(0, data_source.size(0) - 1, bptt):
            data, targets = get_batch(data_source, i, bptt)
            output, hidden = model(data, hidden)
            output_flat = output.view(-1, ntokens)
            total_loss += len(data) * criterion(output_flat, targets).item()
            hidden = repackage_hidden(hidden)
    return total_loss / (len(data_source) - 1)


def test(model, data_source, ntokens, eval_batch_size, bptt, criterion, epoch):

    model.eval()
    total_loss = 0.
    hidden = model.init_hidden(eval_batch_size)
    correct = 0.
    total_test_words = 0.
    with torch.no_grad():
        for i in range(0, data_source.size(0) - 1, bptt):
            data, targets = get_batch(data_source, i, bptt)
            output, hidden = model(data, hidden)
            output_flat = output.view(-1, ntokens)
            pred = output_flat.data.max(1)[1]
            correct += pred.eq(targets.data).sum().to(dtype=torch.float)
            total_test_words += targets.data.shape[0]
            total_loss += len(data) * criterion(output_flat, targets).item()
            hidden = repackage_hidden(hidden)

    acc = 100.0 * (correct / total_test_words)
    loss = total_loss / (len(data_source) - 1)
    print(f"Epoch: {epoch}, Accuracy: {acc}, Loss: {loss}")
    return acc.item()


def serve_helper(model, data_source, eval_batch_size, bptt, ntokens):
    model.eval()
    total_loss = 0.
    hidden = model.init_hidden(eval_batch_size)
    correct = 0.
    total_test_words = 0.
    # get the last batch:
    i = data_source.size(0) - 2
    with torch.no_grad():
        data, targets = get_batch(data_source, i, bptt)
        output, hidden = model(data, hidden)
        output_flat = output.view(-1, ntokens)
        pred = output_flat.data.max(1)[1]
    return pred


def train_helper(model, train_data, ntokens, batch_size, bptt, criterion, epoch, lr, log_interval, clip):

    model.train()
    total_loss = 0.
    start_time = time.time()
    hidden = model.init_hidden(batch_size)
    for batch, i in enumerate(range(0, train_data.size(0) - 1, bptt)):
        data, targets = get_batch(train_data, i, bptt)
        # Starting each batch, we detach the hidden state from how it was previously produced.
        # If we didn't, the model would try backpropagating all the way to start of the dataset.
        hidden = repackage_hidden(hidden)
        model.zero_grad()
        output, hidden = model(data, hidden)
        loss = criterion(output.view(-1, ntokens), targets)
        loss.backward()

        # `clip_grad_norm` helps prevent the exploding gradient problem in RNNs / LSTMs.
        torch.nn.utils.clip_grad_norm_(model.parameters(), clip)
        for p in model.parameters():
            p.data.add_(-lr, p.grad.data)

        total_loss += loss.item()

        if batch % log_interval == 0 and batch > 0:
            cur_loss = total_loss / log_interval
            elapsed = time.time() - start_time
            print('| epoch {:3d} | {:5d}/{:5d} batches | lr {:02.2f} | ms/batch {:5.2f} | '
                  'loss {:5.2f} | ppl {:8.2f}'.format(
                epoch, batch, len(train_data) // bptt, lr,
                              elapsed * 1000 / log_interval, cur_loss, math.exp(cur_loss)))
            total_loss = 0
            start_time = time.time()

def train_dp_helper(model, train_data, ntokens, batch_size, bptt, criterion, epoch, lr, log_interval, S, sigma):

    model.train()
    num_microbatches = 20
    total_loss = 0.
    start_time = time.time()
    hidden = model.init_hidden(batch_size)
    for batch, i in enumerate(range(0, train_data.size(0) - 1, bptt)):
        data, targets = get_batch(train_data, i, bptt)
        # Starting each batch, we detach the hidden state from how it was previously produced.
        # If we didn't, the model would try backpropagating all the way to start of the dataset.
        hidden = repackage_hidden(hidden)
        model.zero_grad()
        output, hidden = model(data, hidden)
        loss = criterion(output.view(-1, ntokens), targets)
        losses = torch.mean(loss.reshape(num_microbatches, -1), dim=1)
        saved_var = dict()

        for tensor_name, tensor in model.named_parameters():
            saved_var[tensor_name] = torch.zeros_like(tensor)
        for pos, j in enumerate(losses):
            j.backward(retain_graph=True)
            total_norm = torch.nn.utils.clip_grad_norm_(model.parameters(), S)

            for tensor_name, tensor in model.named_parameters():
                if tensor.grad is not None:
                    new_grad = tensor.grad
                saved_var[tensor_name].add_(new_grad)
            model.zero_grad()

        for tensor_name, tensor in model.named_parameters():
            if tensor.grad is not None:
                saved_var[tensor_name].add_(torch.FloatTensor(tensor.grad.shape).normal_(0, sigma))
                tensor.grad = saved_var[tensor_name] / num_microbatches
        for p in model.parameters():
            p.data.add_(-lr, p.grad.data)

