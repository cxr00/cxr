# cxr.state

`cxr.state` started as a wrapper class for processing state-based events in pygame, but quickly grew into a general purpose state management module. Despite being the shortest module at the start, it quickly became the most crucial part of `cxr.game` before being generalized. Notably, it led to the deprecation of `cxr.game.room`, in favor of a more generalized implementation.

StateManagers abstract away the assignment and execution of  **state** functions, which govern what happens during the game loop, and **controller** functions, which control the current state.

The data contained in StateManager objects serializes to Qoid. It is highly recommended that you are familiar with Qoid syntax if you want to make full use of serialization.

## Overview

Classes encapsulated in parens `()` do not need to be interacted with except by contributing developers. However, parenthetical classes are basically feature complete so no further developer interaction should be necessary.

```
(Qoid -> StateData) -> StateManager -> StateManagerReference <- (CXRNode <- dag.Node)
```

### Creating a player controller with StateManager

Let's start by generating a StateManager object for a player. StateManager can be directly imported from both `cxr.state` and `cxr` itself as SM:

```python
from cxr SM, SMR
import pygame

# This is required at the beginning
# Don't worry about what it does for now, just know that it is necessary
SMR.initialize("root")

player = SM.generate("player", key="player1")
```

We use `generate` with a name parameter to create a StateManager with a unique key and the name player. Each StateManager has a unique key because there is a global reference of all StateManagers that currently exist. This key is generated randomly, but you should give it a specific one with `key=value`, especially if you are planning on saving & loading.

We now need to set a controller. To do this, we user the `controller` decorator on a function with a single argument `event`. We configure this controller to respond to the four arrow keys:

```python
@player.controller
def player_controller(event):
    if event.type == pygame.KEYDOWN:
        if event.key == pygame.K_UP:
            player.change_state("up")
        elif event.key == pygame.K_DOWN:
            player.change_state("down")
        elif event.key == pygame.K_LEFT:
            player.change_state("left")
        elif event.key == pygame.K_RIGHT:
            player.change_state("right")
    elif event.type == pygame.KEYUP:
        if not any(pygame.key.get_pressed()):
            player.change_state("neutral")
    elif event.type == pygame.QUIT:
        exit(0)
```

We use `change_state` to tell the StateManager to change which state will be activated during the game loop. In this case, the event is a pygame event, but you can substitute it for anything - a class, a tuple, a dict. The only condition is that the controller (as well as states and checks) must have exactly one argument.

Next, let's create our four state functions and add them to the player using the `add_state` decorator:

```python
@player.add_state("neutral")
def neutral_state(event):
    pass


@player.add_state("up")
def up_state(event):
    print("up")


@player.add_state("down")
def down_state(event):
    print("down")


@player.add_state("left")
def left_state(event):
    print("left")


@player.add_state("right")
def right_state(event):
    print("right")
```

Now, depending on whether a specific key is pressed, a different output will be printed. If no key is pressed, then nothing is printed. It should also be noted that the first state that we add becomes the default state, so we started by adding neutral.

In addition to a controller, we can add additional checks to StateManagers:

```python
@player.check
def player_check(event):
    # Additional logic here
    pass
```

When executing calls, checks are performed *after* the controller and state functions, in the order they were added. In many cases a controller should be enough, but checks are there to help organize your code.

Now that we have built a player StateManager, we can put it into action. First, we'll write some boilerplate pygame code:

```python
pygame.init()
WIDTH = 600
HEIGHT = 480
size = WIDTH, HEIGHT
screen = pygame.display.set_mode(size)
```

Finally, we can create the core game loop:

```python
while True:
    # Guarantee at least one event
    pygame.event.post(pygame.event.Event(pygame.USEREVENT))
    events = pygame.event.get()
    for event in events:
        for sm in SM.all():
            sm(event)
    pygame.display.update()
    pygame.time.wait(17)  # 60 FPS
```

When run, the console will print up, down, left, or right when you press an arrow key.

We iterate over all the pygame events, then over `StateManager.all()`, which is a list of all created StateManagers (in this case, just our player).  StateManagers can be called like functions, so within the inner loop we call the StateManager with the event as an argument, which then decides what to do according to current state.

### Setting and getting StateData

Each StateManager is equipped with a StateData object, a dictionary which distinguishes between serializable and nonserializable data. Data can be set and retrieved using `__getitem__` and `__setitem__`:

```python
player["height"] = 72
print(player["height"])
```

Data can also be accessed via `__getattr__`, **but CANNOT be set with** `__setattr__`:

```python
print(player.height)

player.height = 20  # THIS DOES NOT WORK
```

The reason for this is due to the way StateData access is implemented. Unfortunately, attempting to add a `__setattr__` override causes a `RecursionError`.

In general, when assigning values to the StateData, it will automatically determine if the value is serializable or not. However, if you want to specifically add an attribute as nonserializable, use `nonser`:

```python
player.nonser("weight", 167)
```

### StateManager static methods

In addition to a global reference, StateManager comes equipped with a variety of static methods to interact with your SMs. It also includes serialization to Qoid. I would highly recommend reading the documentation in `cxr.game.state`. But, for ease of access, here is a summary of what can be done:

`all` - Get a list of every SM that currently exists

`get` - Get a specific SM by key

`delete` - Delete an SM by reference or key

`generate_key` - Generate a unique key for an SM. This is automatically called by `generate`

`generate` - Create a new StateManager at the given location

`reset` - Clear the global SM reference

### Custom extensions of StateManager

If your desired StateManager object has its own class, then you can submit the class as a parameter of `StateManager.generate`:

```python
player = StateManager.generate("player", Player, "player1")
```

Notice the inclusion of a tertiary argument `"player1"`. This is the *key* assigned to a particular StateManager which is otherwise randomly generated. This allows quick access to the player SM via `StateManager.get("player1")`.

## StateManagerFactory

If you need to create a lot of a specific type with the same parameters, use a `StateManagerFactory`:

```python
from cxr import SMF

my_factory = SMF("mytype", MyType, randomise=False)

my_type_instances = []
for i in range(10):
    my_type_instances.append(my_factory.make())
```

This will construct 10 instances of `MyType`, with the names `mytype_0` through `mytype_9`. You can also set randomise to True, which will produce instances with keys such as `mytype_1aYe2`. This is useful for intentional obfuscation where specificity is not important. Note that while there are nearly 57 billion possible random keys, the randomiser will give up after about 77k attempts at creating a unique unused key. If you receive that `StateError`, then you got REALLY unlucky.

## StateErrors

In the event that you attempt to access a SM or data within that does not fit, you will receive a `StateError`. StateErrors are simple custom `KeyError` exceptions which indicate that you have attempted to incorrectly access an attribute of the SM. There is currently no additional functionality to this type of exception.

## StateManagerReference

`StateManagerReference` is the utility class for accessing groups of related StateManagers in a file-like way. We start by initializing the SMR at the desired location:

```python
SMR.initialize("your\\location")
```

**The initialization via SMR requires use of backslashes for pathing, BUT `SM.generate` requires forward slashes!**

Within that directory you can generate StateManager instances, either directly within that folder or within subfolders that can be quickly defined:

```python
sm0 = SM.generate("player", Player, "player1")  # Creates file at your\location\player.cxr
sm1 = SM.generate("enemies/beetle", Beetle, "beetle0")  # Creates file at your\location\enemies\beetle.cxr
sm2 = SM.generate("enemies/beetle", Beetle, "beetle1")  # Stored in the same place as sm1
```

Any SM created using `SM.generate` is automatically indexed by SMR. If you had multiple players, for example, you could get them all via `SMR.get("player")`.

```python
for beetle in SMR.get("enemies/beetle"):  # Iterate over all Beetle instances
    pass
```

Besides `initialize` and `get`, there are only two other functions that the average user will need, being `save` and `load`. Both of these methods have **optional parameter saving**, where only the specified tags are updated. The default behavior is to save or load *all* attributes.

```python
SMR.load("player")  # Loads all attributes of each player within the reference
SMR.save("enemies/beetle", "hp", "def")  # Saves only hp and def attributes of each Beetle in the reference
```

The remaining functions are not necessary for normal operation, but you are free to look at their documentation.

It's important to note that as you expand your game with new StateManagers, the event loop will stay quite small, since `StateManager.all` does the heavy lifting. However, realize that this game loop is submitting *all* events to *every* StateManager. It is more likely that you will divide this up to keep the time complexity from reaching `O(n**2)`:

```python
import pygame.event

for event in events:
    if event.type == pygame.KEYDOWN:
        for sm in SMR.get("player"):
            sm(event)
    elif event.type == TICK:  # Custom event made with pygame.event.custom_type()
        for sm in SMR.get("player"):
            sm(event)
        for sm in SMR.get("enemies/beetle"):
            sm(event)
```

This structure ensures that only the Player instance processes KEYDOWN events, while TICK events are processed by the Player and by all existing Beetles. **IN GENERAL, it is a good idea to define a custom TICK event and use it for all NPC and environmental StateManagers.**

### find_by functions

SMR contains two powerful functions which enable a deeper search at a particular location. They are called `find_by_attribute` and `find_by_function`. I'll illustrate with a simple example; Let's say that you want to check for Beetle instances whose `status_condition` is poison. We can iterate over just those Beetle instances like so:

```python
for beetle in SMR.find_by_attribute("enemies/beetle", "status_condition", "PSN"):
    beetle.take_damage(2)
```

We can take this a step further using `find_by_function`. Instead of simply looking for a matching attribute, we specify a function with lambda syntax and iterate through that:

```python
for beetle in SMR.find_by_function("enemies/beetle", "status_condition", lambda x: x != "NORMAL"):
    if beetle.status_condition == "PSN":
        beetle.take_damage(2)
        beetle["status_timer"] -= 1
        if beetle.status_timer <= 0:
            beetle["status_condition"] = "NORMAL"
    elif beetle.status_condition == "BRN":
        beetle.take_damage(3)
        beetle["attack"] -= 1
        beetle["status_timer"] -= 1
        if beetle.status_timer <= 0:
            beetle["status_condition"] = "NORMAL"
            beetle["attack"] += 2
```

We've endowed this loop with more complex behavior; It searches for all instances of abnormal status among beetles and performs actions accordingly. If poisoned, it simply takes damage, but a burn causes damage and decreases attack. In both cases a check is performed on the `status_timer` attribute to determine if its status goes back to normal.

It's up to you to decide where this functionality best fits - personally, I would elect to perform this as a `check` for some environment StateManager.

### Serialization with Qoid

Qoid is a simple markup language optimized for handling primitive types in Python. This means any int, str, tuple, list, and dict is serializable. You also have the option of storing the results of `__repr__` for your own class so they can be reconstructed on the fly.

Qoid syntax is very easy to grasp:

```
/ The entire file is called a Bill
/ Comments are indicated with a forward slash
/ Property -> Qoid -> Bill -> Register (unused)

#Qoid
Property: Value
Property: Value
```

When working with any object in Qoid, using the `inst.get(tag)` function will return the *first* occurrence of the given tag; Use `inst.all_of(tag)` to get every occurrence of a Qoid tag. The same goes for instances of Qoid within a Bill.

Qoid has a folder-like class called a Register, but that class is unused in `cxr.state`.
