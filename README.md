This library was inspired by multiple different mocking frameworks I was
working with. They all come from completely different worlds such as Java,
JavaScript, C++ and C#.


Here is a simple example how mocking of a time.time() can be done:


```Python

import vmock
import time
v = vmock.VMock()
time_mock = v.mock_method(time, 'time')
time_mock().returns(1)
<vmock.mockcallaction.MockCallAction object at 0x103ca1780>
time_mock().returns(2).twice()
<vmock.mockcallaction.MockCallAction object at 0x103ca1eb8>
v.replay()
time.time()
1
time.time()
2
time.time()
2
v.verify()
v.tear_down()
time.time()
1408850749.91605
```


Even more, VMock can create snapshots of class definitions and object
generating virtual code for them, thus you don't need to mock each method
separately. Even more, it mimics their interface so, any interface change
will result in not working test if there is a call mismatch.

