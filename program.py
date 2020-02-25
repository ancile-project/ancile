remote_program = '''
model = data_policy_pairs.pop()
reddit_data = databox.get_latest_reddit_data(session="")
trained_model = federated.train_local(model=model, data_point=reddit_data)
result.return_to_web(dpp=trained_model)
'''
total_participant_dpps = federated.select_users(user_count=312)
client = federated.RemoteClient(callback=federated.accumulate)
model = federated.new_model(policy="ANYF*")

rounds = 1
while rounds:
    rounds = rounds - 1
    participants_data = general.sample_data_policy_pairs(
                            data_policy_pairs=total_participant_dpps,
                            sample_number=312)
    
    while participants_data:
        participant_dpp = participants_data.pop()
        client.send_to_edge(model=model,
                            participant_dpp=participant_dpp,
                            program=remote_program)
    accumulated = client.poll_and_process_responses()
    model = federated.average(accumulated=accumulated, model=model, enforce_user_count=312)
