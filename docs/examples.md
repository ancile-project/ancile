# New additions:

1. Conditions:

    *Syntax*: `condition(field, operation, value)`. Followed by
    `enforce_true` and `enforce_false` operations.

    *Effect*: Enforces that the DataPolicyPair meets certain criteria,
    before advancing the policy.

 1. Conditions on the other DPP:

    *Syntax*: if DPP_1 depends on the value from another DPP_2 the policy for DPP_1 should specify: `condition_dependent(field='oh', operation='eq', value=True, datasource='google', username='same', time='same')`. Whereas DPP_2 can just have `comparison`.
    
    *Effect*: the program has to call `condition` method and supply the correct arguments along with param: `dependent_dpp=dpp_1`.

1. Collections:
    
    *Syntax*: 
    * `get_collection(users, datasource)` - retrieves data for
    set of users and a specific datasource.
    * `get_empty_collection([dpp_1, dpp_2, etc])` - creates a collection
      with policy `ANYF*`
    * `get_collection_policy(user, datasource)` - returns an empty
      collection.
    




## Ancile Program

An application is allowed to submit a program in Python  -- a sequence of commands executed by Ancile. The goal of the program is to consume data from data sources. However, each command in the program is only executed on data if it satisfies the associated policy.

The program can use two objects that Ancile exposes: `user_ctx` and `result`. Ancile as well exposes modules with commands enforceable by policies that will be used to interact with both objects. Additionally, Ancile exposes methods for external interactions that take `user_ctx` object with the name of a data source and produce a `DataPolicyPair` that binds incoming data with the corresponding policy.

`DataPolicyPair` - an object of this class binds policy and data, none of the fields can be accessed from the program. The only way this object can be modified is if it passed as an argument to one of Ancile provided methods and the associated policy allows execution of this method.

`user_ctx` - an object that stores all policies, access tokens, and active DataPolicyPairs. Commands that can fetch data will take this object as a parameter and output a DataPolicyPair.


**command** - a trusted implementation of some functionality that takes data as an input. Each command is either:

1. **External Calls to Data Sources** (policy name:`fetch`) - commands that call data source and return a `DataPolicyPair` (take `user_ctx` as an argument). On data ingress a policy is associated with incoming data. The policy can specify what external calls are allowed or just say `fetch` to allow all external commands for this datasource. The external call can only be the first command that creates a data policy pair. 

2. **Transformation** (policy name:`transform`) -  a command that generates derived data (e.g., transform, test, or aggregate data), take `DataPolicyPair` as an argument:
        * Transformations - any methods that modify, filter, delete data in DataPolicyPair
        * Test/Comparison - checks the value of data and raises an exception if comparison failed
        * Aggregation - methods that take multiple DataPolicyPairs as an argument and combines all of them. Ancile performs policy check based on the union of policies of all supplied `DataPolicyPair`s.
        * Comparison - performs comparison of data values and returns a result of it to the program. This operation is used to allow both policy and program branching.

2. **Use/Returns** (policy name: `return`)- has two calls that allow returning data once policy of DataPolicyPair object has finished:
    * `return_to_the_program` - returns data to the program
    * `append_to_result` - adds data to the result that will be sent to the application

Isolation: Each transformation command doesn’t return any data back to the program, but only modifies the DataPolicyPair object that can’t be modified or viewed by the program. Similarly user_ctx object can’t be modified and only exposes a method get_empty_dp. This trick allows us to not expose any data to the program without the explicit calling of Use method. Commands that return data have to be `uses`.

Ancile exposes commands that are organized into Python modules, i.e. (indoor location, machine learning, etc) and the policy can just specify that it allows all methods from this module. Additionally, the policy can simply say transform or return to allow any methods tagged as transform or return. 

## Room Booking

Idea: Book rooms based on indoor user location
Sensitive data: Location data, Calendar Access
*This example demonstrates basic protection of fields and data access functions*

Prevent leakage of detailed location data (data source: **Indoor Location**):

### Functions
* type: fetch: 
    * `indoor.fetch_recent_location()` - calls data service and populates data with location coordinates for the user.
    * `azure.book_room(room)` - books a room
* type: transform: 
    * `general.drop_keys(key_list)` - goes through the data object and drops all keys in key_list.
* type: return: 
    * `result.append_dp_data_to_result(data)` - Appends data to the object that will be returned to the application.



### Policy

commands: 
* `ANYF*` - allows all functions
* `return` - allows all return functions
 
This policy allows fetching data but requires to drop sensitive keys and allows any other transformations afterwards.
```python
p1 = fetch_recent_location
        .drop_keys(['lat', 'long', 'netID'])
        .ANYF*
        .return
```
### Program
```python
dp_1 = indoor.fetch_recent_location(user_ctx=user_ctx['user'],           
            data_source='campus_data_service')
general.drop_keys(data=dp_1, ['lat', 'long', 'netID'])
result.append_dp_data_to_result(data=dp_1)
```


### Example
```python    
# original data
v= {'netID': 'user', 'lat': 0, 'long': 0, 
            'floor': 'Third Floor', 'building': 'Bloomberg'}
#after dropping keys
v= {'floor': 'Third Floor', 'building': 'Bloomberg'}
```

Allow only booking rooms or checking available rooms for data source **Outlook** :
Policy:
`p2 = (book_room+available_room).ANYF*.return`
Program:
```python
dp_list = azure.book_room(user_ctx=user_ctx['user'], 
        data_source='outlook', room=’room_email’)
result = use_type.return_to_the_program(data=dp_list)
if result['available'] == True:
    dp_2 = azure.book_room(user_ctx=user_ctx['user'], 
            data_source='outlook', room=’room_email’)
result.append_dp_data_to_result(data=dp_1)
```

## Office Hours

Idea: Allow the application to see whether the professor is on campus during office hours
Sensitive data: Access to calendar, location data
This example demonstrates aggregation of data - calendar event, location geofence. And testing values of data.

### Functions

* fetch
    * `google.get_calendar_events()` - retrieves all current calendar events from the Google Calendar server. 
    * `location.get_recent_location_data()`
    * `location.get_in_geofence(x, y, radius)` - calls Vassar server to retrieve if the user is within the geofence.
* transform
    * `general.aggregate()` - aggregates together all data sources and policies. Authorized aggregation transformation produces data-policy pairs comprised of combined data paired with the intersection of the derivative policies. The result is stored inside `user_ctx['aggregate']`.
    * `location.in_geofence(x, y, radius)` - creates a new boolean field `in_geo` with the result of testing the coordinates to be within the geofence.
    * `google.event_occurring(event_title)` - checks whether the event with the name `event_title` is happening
    * `general.test_true(key, op='eq', value=True)` - if `op(key, value)` returns `True` the call succeeds, otherwise an exception is raised and execution stopped
    * `general.test_false(key,  op='eq', value=True)` - if `op(key, value)` returns `False` the call succeeds, otherwise an exception is raised and execution stopped
    * `general.keep_keys(key_list)` - goes through the data object and drops all keys in key_list.
    * `comparison(key, value, op)` - returns the result of comparing the `key` in data with `value` using operation `op`

### Policy

Policy for datasource **Google** only allows to check if the event `event_name` is happening now:
```python
p_google = get_calendar_events()
.event_occurring(event_title='event_name')
.comparison(key='occurring', value=True, op='eq')
.(
    test_true(key='occurring').keep_keys(keys=['occurring']).aggregate().return 
    + test_false(key='occurring').0 
)
```
We are using a trick to allow the program to check the value of the data value before enforcing it. The program can run first `comparison` and based on the returned result execute either `test_true` or `test_false`. It allows to have a workflow that is more smooth and doesn't raise unnecessary exceptions. Additionally, we can make a `comparison` function to be more powerful and advance the policy by calling either `test_true` or `test_false`.

For datasource **Vassar CDS** there are two fetch functions: `get_recent_location_data` and `get_in_geofence`. Therefore we can create two policies that check if the user is currently within the geofence:

1. Policy that uses `get_recent_location_data`
    ```python
    p1 = get_recent_location_data.
    in_geofence(x=0, y=0, radius=10)
    .comparison(key='in_geo', value=True, op='eq')
    .(
        test_true(key='in_geo').keep_keys(keys=['in_geo']).aggregate.return 
        + test_false(key='in_geo').0 
    )
    ```
2. Policy that uses `get_in_geofence`:
    ```python
    p2 = get_in_geofence(x=0, y=0, radius=10)
    .comparison(key='in_geo', value=True, op='eq')
    .(
        test_true(key='in_geo').keep_keys(keys=['in_geo']).aggregate.return 
        + test_false(key='in_geo').0 
    )
    ```

Therefore a user for data source **Vassar CDS** can have a combined policy: `p1 + p2` or if simplified: 
```python
p_vassar = 
    (
        get_recent_location_data.in_geofence(x=0, y=0, radius=10) \
        + get_in_geofence(x=0, y=0, radius=10)
    )
    .comparison(key='in_geo', value=True, op='eq')
    .(
        test_true(key='in_geo').keep_keys(keys=['in_geo']).aggregate.return 
        + test_false(key='in_geo').0 
    )
```

---
### Nate's examples :
Example #1
`v = { NetID = “jnf27”, lat = 0.0, long = 0.0 }`
Intended policy does two things:
Filters to a geofence (say, the unit circle)
Drops other keys (say, lat and long)
```
ANY* . filter_geofence_circle(1.0) . ANY* . 
        drop_keys([“lat”, “long”]) . ANY* . return
```
Example #2
`v = { NetID = “jnf27”, type = “in” / “out” }`
`p = ANY* . [test_in() . ANY* . return + test_out() . 0]`

Union can be used to combine different policies, and this may make get_* functions useful as a convention.
```
get_google_data .  ...
+ 
get_aruba_data . ...
```

Execution:
* New tuple arrives in the system (like v above)
* Form the pair <v, p>
* Program executes several functions like in_geofence
* And finally attempts a use

---

### Program
```python

dp_v = location.get_recent_location_data(
                    user_ctx=user_ctx['user'], 
                    data_source='google')

location.in_geofence(data=dp_v, x=0.0, y=0.0, radius=10)
if comparison(data=dp_v, key='in_geo', value=True):
    general.test_true(data=dp_v, 'in_geo')
    general.keep_keys(data=dp_v, 'in_geo')
    
    dp_google= google.get_calendar_events( 
                            user_ctx=user_ctx['user'],
                            data_source='google')
    google.event_occurring(data=dp_google, event_title='event_name')
    if comparison(data=dp_google, key='occurring', value=True):
        general.test_true(data=dp_google, 'occurring')
        google.keep_keys(keys=['occurring'])
        dp_aggregate = general.aggregate(data=[dp_v, dp_google])

        result.append_dp_data_to_result(data=dp_aggregate)
    
    
    
```

### Example
```python
# initial data
dp_v._data =  { NetID = “jnf27”, lat = 0.0, long = 0.0 }
# after comparison
dp_v._data = {'in_geo', True}

#initial data
dp_google = {'some google metadata'}
# after comparison
dp_google._data = {'occurring': True}

# resulting data
dp_aggregate._data = {'in_geo', True, 'occurring': True}

```    


## Study Group

Idea: Know when other members of your group are on campus notify everyone
Sensitive data: Individual user locations
Group Events: All users are inside the geofence
This example demonstrates aggregation of data sources across multiple users.

### Functions

Same as before, except:
* transform
    * `aggregate_enforce_participants(participants, key, data_source)` - aggregates data from participants and checks that DataPolicyPairs supplied match `participants` and were created for `data_source`. During aggregation the method checks that each data object has `key` that equals  `True`. Similarly, `aggregate_enforce_partial(n, key)` can enforce when at least `n` participants have `key` equals `True`.


### Policy

The policy enforces release of the data, when all of the participants are on campus. Released data is a flag that both users are on campus. 
```python
in_geofence(data=dp_v, x=0.0, y=0.0, radius=10).
keep_keys(keys=['in_geo']).
.aggregate_enforce_participants(participants=['user1', 'user2'],
                                key='in_geo', data_source='location')
.return
```

### Program

```python
dp_1 = location.in_geofence(user_ctx=user_ctx['user1'], 
        data_source='location',
        data=dp_v, x=0.0, y=0.0, radius=10)
general.keep_keys(data=dp_1, keys=['in_geo'])        

dp_2 = location.in_geofence(user_ctx=user_ctx['user2'], 
        data_source='location',
        data=dp_v, x=0.0, y=0.0, radius=10)
general.keep_keys(data=dp_2, keys=['in_geo'])        

dp_aggr = general.aggregate_enforce_participants(data=[dp_1, dp_2], 
                                participants=['user1', 'user2'],
                                key='in_geo', data_source='location')

result.append_dp_data_to_result(data=dp_aggregate)
```


## Daily activity

Idea: Release daily statistics data
Sensitive data: releasing individual data points can be harmful
This example demonstrates long-running policies that span over multiple API calls

All unfinished policies will be persisted within Ancile. After calling `aggregate` method a new object is created in `user_ctx['aggregate']`. Additionally every method `general.aggregate()` - only aggregates distinct DataPolicyPairs  preventing duplicates.

### Functions
* `user_ctx[‘aggregate’].get_existing_dp(‘aggregate’)` - retrieves DataPolicyPair with name aggregate that was persisted from the previous call
* transform
    * `compute_location_statistics()` - computes statistics over an array of data
    * `general.counter()` - a simple counter that updates a `counter` field in the data object


### Policy:

This policy allows to return statistics on data points when there are at least 50 points aggregated. Additionally, it's possible to implement enforcement over time intervals to guarantee breaks between data calls.
```python
fetch_recent_location.(aggregate.counter)*
.comparison(key='counter', value=True, op='eq')*
    .(
        test_true(key='counter', op='geq', value=50)
            .compute_location_statistics
            .return 
        + test_false(key='counter', op='geq', value=50).0 
    )
```

### Program
```python
# First N-1 API Calls: 
dp_1 = indoor.fetch_recent_location(user_ctx=user_ctx['user'],
            data_source='campus_data_service')
if general.user_ctx.get(‘aggregate’, False):
    old_dp = user_ctx[‘aggregate’].get_existing_dp(‘aggregate’)]
    dp_aggr = general.aggregate(data=[dp1, old_dp] )
else:
    dp_aggr = general.aggregate(data=[dp1])
general.counter(dp_aggr)

# Last API Call: 
dp_aggr = user_ctx['aggregate'].retrieve_existing(data_source=‘aggregate’)
if comparison(data=dp_aggr, key='counter', op='geq', value=50):
    general.test_true(data=dp_aggr, key='counter', op='geq', value=50)
    indoor_location.compute_location_statistics(data=dp_aggr)
    result.append_dp_data_to_result(data=dp_aggr)
```

## Encryption example

Allow delayed release of data with dropping certain fields in the end. The encrypted data will be sent to the app (each field with the different key). When the program executes `return` Ancile returns only the encryption keys.



### Functions
* transform
    * `flatten` - converts hierarchical data object into a dict so encryption can encrypt each field separately.
* return
    * `append_dp_data_to_result(decrypt_field_list)` - returns encryption keys for specified fields.

### Policy
Policy allows fetching 
```python
fetch_recent_location.(aggregate.flatten.counter)*
.comparison(key='counter', value=50, op='geq')*
    .(
        test_true(key='counter', op='geq', value=50)
            .append_dp_data_to_result(decrypt_field_list=['x', 'y']) 
        + test_false(key='counter', op='geq', value=50).0 
    )
```

### Program

```python
# First N-1 API Calls: 
dp_1 = indoor.fetch_recent_location(user_ctx=user_ctx['user'],
            data_source='campus_data_service')
if general.user_ctx.get(‘aggregate’, False):
    old_dp = user_ctx[‘aggregate’].get_existing_dp(‘aggregate’)]
    dp_aggr = general.aggregate(data=[dp1, old_dp] )
else:
    dp_aggr = general.aggregate(data=[dp1])
general.counter(dp_aggr)

# Last API Call: 
dp_aggr = user_ctx['aggregate'].retrieve_existing(data_source=‘aggregate’)
if comparison(data=dp_aggr, key='counter', op='geq', value=50):
    general.test_true(data=dp_aggr, key='counter', op='geq', value=50)
    
    result.append_dp_data_to_result(data=dp_aggr, 
                                    decrypt_field_list=['x', 'y'])

```

`counter` currently is designed to save data inside the data object which will be encrypted and sent to the app. I can make a separate "technical" storage for variables that won't be encrypted and will be saved within Ancile.



## Machine Learning

Example. Machine Learning
Idea: train ML model on private data from different participants and serve it for future predictions
Sensitive data: Data, ML model

This example demonstrates that the usage policy can apply to ML models as a form of data transformation.

### Functions
* fetch
    * `get_split_train_mnist(split, part)` - artificial method that fetches a part of the MNIST dataset equally split among participants
* transform
    * `aggregate_train_dataset()` - combines data from supplied parts of the dataset
    * `get_test_mnist()` - downloads a test dataset
    * `get_loader(dataset_name, batch_size)` - creates dataset loader (specific to PyTorch)
    * `create_model()` - creates ML model with preset structure
    * `sgd_optimizer(lr, momentum)` - creates SGD optimizer
    * `nll_loss()` - creates a loss object
    * `pickle_model()` - prepare the model to be persisted within Ancile
    * `train_one_epoch(epoch, log_interval)` - perform normal training for one epoch
    * `test(epoch)` - calculate accuracy of the model on test set
    * `get_prediction(image_id)` - compute prediction on the image (`image_id` from the test set)


### Policy
We allow to use the model to be trained on aggregated data. As well, the application can stop any time but should call `pickle_model` to persist the model. After the training we allow to run prediction on data and only return the result of this prediction.
```python
get_split_train_mnist
.aggregate_train_dataset*
.get_test_mnist
.(
    create_or_load_model
    .sgd_optimizer
    .nll_loss
    .(train_one_epoch.test )*
)*
.(get_prediction.keep_keys(keys=[‘predictions’]).return)*
```

### Program
```python
# First API Call:
deep_learning.get_split_train_mnist(user_ctx["user1@abcd.com"], 
                                    data_source='mnist', 
                                    data=dp_1, split=2, part=0)
deep_learning.get_split_train_mnist(user_ctx["user2@abcd.com"], 
                                    data_source='mnist', 
                                    data=dp_2, split=2, part=1)

aggr_dp = deep_learning.aggregate_train_dataset(data=[dp_1, dp_2])

deep_learning.get_test_mnist(data=aggr_dp)

deep_learning.get_loader(data=aggr_dp, dataset_name='train', batch_size=64)
deep_learning.get_loader(data=aggr_dp, dataset_name='test', batch_size=100)

deep_learning.create_or_load_model(data=aggr_dp)
deep_learning.sgd_optimizer(data=aggr_dp, lr=0.1, momentum=0.9)
deep_learning.nll_loss(data=aggr_dp)

for epoch in range(1):
    deep_learning.train_one_epoch(data=aggr_dp, epoch=epoch, log_interval=200)
    deep_learning.test(data=aggr_dp, epoch=epoch)


# Next API calls:
aggr_dp =user_ctx['aggregate'].retrieve_existing_dp()
deep_learning.create_or_load_model(data=aggr_dp)
deep_learning.sgd_optimizer(data=aggr_dp, lr=0.1, momentum=0.9)
deep_learning.nll_loss(data=aggr_dp)

for epoch in range(10):
    deep_learning.train_one_epoch(data=aggr_dp, epoch=epoch, log_interval=200)
    deep_learning.test(data=aggr_dp, epoch=epoch)

deep_learning.get_prediction(data=aggr_dp, image=10)
general.keep_keys(data=aggr_dp, keys=['prediction'])
result.append_dp_data_to_result(data=aggr_dp)
```

### Extensions

* Differential Private Training
* Obfuscating output
* Enforcing limits on data used for training



## Additional: Dwell Time

Idea: release data only after a person was in the location for more than 5 minutes. 

### Function

* transform
    * `aggregate_record_state(key, target, timestamp)` - takes two DataPolicyPairs: new data and aggregate object and appends the value `key` to the `target` field of the aggregate object. Can keep `(value, timestamp)` for each added key.
    * `compute_consistent_value_over_interval(val_list, interval, value)` - a method that can look at the list `val_list` and identify if the values within `interval` were all equal to value. The result is recorded into `consistent_value` field.
    * `clean_values(val_list, interval)` - removes all values beyond specified time interval from the list `val_list`.

### Policy

```python
get_in_geofence(x=0, y=0, radius=10)
( 
  .aggregate_record_state(key='in_geo', 
                          target='in_geo_list', 
                          timestamp=True)
  .compute_consistent_value_over_interval(val_list='in_geo_list', 
                                          interval=300)
  .clean_values(val_list='in_geo_list', interval=300)
  .comparison('consistent_value', value=True, op='eq')
  .(
     test_false('consistent_value').0
     + test_true('consistent_value')
       .keep_keys(keys=['consistent_value'])
       .return
  )
)*
+ return

```

Explanation: the program will every time try to fetch data, and the only response it will get if the user was located within the geofence for at least 5 minutes. As we use aggregation method we need to allow the repeated aggregation, therefore we add `*` to the sequence of commands.

### Program

This program can be executed multiple times and the policy will still keep running. 

```python
dp_1 = indoor.get_in_geofence(user_ctx=user_ctx['user'],           
            data_source='campus_data_service', x=0, y=0, radius=10)

aggr_dp =user_ctx['aggregate'].retrieve_existing_dp()

aggr_dp = aggr.aggregate_record_state(data=[dp, aggr_dp], key='in_geo', 
                              target='in_geo_list', 
                              timestamp=True)
                              
aggr.compute_consistent_value_over_interval(data=dp_aggr,
                                        val_list='in_geo_list', 
                                        interval=300)
aggr.clean_values(data=dp_aggr, val_list='in_geo_list', interval=300)
if comparison(data=dp_aggr, 'consistent_value'):
    test_true('consistent_value')
    result.append_dp_data_to_result(data=dp_aggr)
```

