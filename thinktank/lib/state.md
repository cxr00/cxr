## cxr.state

`cxr.state` started as a wrapper class for processing state-based events in pygame, but quickly grew into a general purpose state management module. Despite being the shortest module at the start, it quickly became the most crucial part of `cxr.game` before being generalized. Notably, it led to the deprecation of `cxr.game.room`, in favor of a more generalized implementation.

StateManagers abstract away the assignment and execution of  **state** functions, which govern what happens during the game loop, and **controller** functions, which control the current state.

The data contained in StateManager objects serializes to Qoid. It is highly recommended that you are familiar with Qoid syntax if you want to make full use of serialization.

### Creating a player controller with StateManager

Let's start by generating a StateManager object for a player:

```python
from thinktank.lib.state import StateManager, StateManagerReference
import pygame

# This is required at the beginning
# Don't worry about what it does for now, just know that it is necessary
StateManagerReference.initialize()

player = StateManager.generate("player")
```

We use `generate` with a name parameter to create a StateManager with a unique key and the name player. Each StateManager has a unique key because there is a global reference of all StateManagers that currently exist.

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

We use `change_state` to tell the StateManager to change which state will be activated during the game loop. 

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

When executing calls, checks are performed *after* the controller function, in the order they were added. In many cases a controller will be enough, but checks are there to help organize your code.

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
    events = pygame.event.get()
    if not events:
        events = [pygame.event.Event(pygame.USEREVENT)]
    for event in events:
        for sm in StateManager.all():
            sm(event)
    pygame.display.update()
    pygame.time.wait(17)  # 60 FPS
```

When run, the console will print up, down, left, or right when you press an arrow key.

We iterate over all the pygame events, then over `StateManager.all()`, which is a list of all created StateManagers (in this case, just our player).  StateManagers can be called like functions, so within the inner loop we call the StateManager with the event as an argument, which then decides what to do according to current state.

It's important to note that as you expand your game with new StateManagers, the event loop will stay quite small, since `StateManager.all` does the heavy lifting.

### Setting and getting StateData

Each StateManager is equipped with a StateData object, a dictionary which distinguishes between serializable and nonserializable data. Data can be set and retrieved using `__getitem__` and `__setitem__`:

```python
player["height"] = 72
print(player["height"])
```

Data can also be accessed via `__getattr__`, but CANNOT be set with `__setattr__`:

```python
print(player.height)

player.height = 20  # Does not work
```

In general, when assigning values to the StateData, it will automatically determine if the value is serializable or not. However, if you want to specifically add an attribute as nonserializable, use `add_nonser`:

```python
player.add_nonser("weight", 167)
```

### StateManager static methods

In addition to a global reference, StateManager comes equipped with a variety of static methods to interact with your SMs. It also includes serialization to Qoid. I would highly recommend reading the documentation in `cxr.game.state`. But, for ease of access, here is a summary of what can be done:

`all` - Get a list of every SM that currently exists

`get` - Get a specific SM by key

`delete` - Delete an SM by reference or key

`find_by_attribute` - Find all SMs which have the given attribute matching the given value

`find_by_function` - Find all SMs where the given attribute returns True when evaluated by a function

`generate_key` - Generate a unique key for an SM. This is automatically called by `generate`

`generate` - Create a new StateManager at the given location

`reset` - Clear the global SM reference
