+++
title = 'Automated Experiment Validation with Pydantic and Type Hints'
date = 2024-10-23
description = 'Configuring an experiment is a key step in quantitative research. In this blog post, we will explore type hinting and data validation with Pydantic to automatically validate the experimental configuration. This allows us to catch locgical inconsitencies before they affect the actual experiment and leads to software that is more robust.'
cover = 'cover.png'
+++

The design of an experiment involves many choices: Which stimuli are displayed? How often are they repeated? What kind of responses are obtained? And so on ...
It is good practice to store these parameters in a configuration, separate from the experimental code.
This allows us to store all parameters in one place and reconfigure the experiment without altering the code.
However, that means that the configuration file carries a lot of responsibility - any error in that file could crash the experiment.
What's more, because Python is a dynamically typed language, the parameters stored in the configuration file are only evaluated once they are accessed.
This means our experiment could start fine despite one parameter being invalid and then crash the first time that parameter is accessed.
This is obviously not ideal - if our experimental configuration is invalid, we would like to know that before running the experiment.
In this blog post I'll show you how to use type-hinting and a library called Pydantic to create robust experiments that are automatically validated.

## Prerequisites

To implement an example experiment, we'll use a psychoacoustics library called soundlab [^1].
To reproduce the examples, you have to install it with `pip install slab`.
Depending on your operating system, additional steps may be required play sounds and record responses - check out [slab's documentation](https://github.com/DrMarc/slab/tree/master?tab=readme-ov-file#installation)
You'll also need Pydantic which you can install with `pip install pydantic`

## Configuring an experiment

As an example we'll implement a pure tone audiogram that uses an adaptive staircase to identify the hearing threshold.
The following code presents a pure tone and then waits for the listener's response ("1" if the sound was heard, "2" if not).
The intensity is decreased until the sound can not be heard, then increased again until it can, then decreased again and so on, until the direction has reversed 10 times.
The threshold is obtained by averaging across all reversal points [^2].

```python
import slab
stimulus = slab.Sound.tone(frequency=2000, duration=0.5)
stimulus = stimulus.ramp(when="both", duration=0.01)
stairs = slab.Staircase(start_val=50, n_reversals=10)
for level in stairs:
    stimulus.level = level
    stairs.present_tone_trial(stimulus, key_codes=(ord("1"), ord("2")))
print(stairs.threshold())
```

This works but any time we'll have to change the code every time we want to reconfigure the experiment.
To avoid this, we can store all of parameters in one file, let's call it `config.json` [^3].
For the audiogram, the content of this file may look like this:

```json
{
    "frequency": 500,
    "stimulus_duration": 0.5,
    "ramp_duration": 0.01,
    "start_val": 50,
    "n_reversals": 10,
    "keys": {"yes":"1", "no":"2"}
}
```

Now, we can load the parameters from `config.json`, and pass them to the audiogram.
Let's implement the loading of the config file and execution of the audiogram in two separate functions.
We'll also add a little command line interface using the `argparse` module that allows us to run our experiment from the terminal.
If we store the code below in a file called `audiogram.py` we can run the experiment from the command line by typing `python audiogram.py config.json`.

```python

from argparse import ArgumentParser
import json
import slab


def audiogram(cfg):
    stimulus = slab.Sound.tone(cfg["frequency"], cfg["stimulus_duration"])
    stimulus = stimulus.ramp(when="both", duration=cfg["ramp_duration"])
    stairs = slab.Staircase(cfg["start_val"], cfg["n_reversals"])
    for level in stairs:
        stimulus.level = level
        stairs.present_tone_trial(
            stimulus, key_codes=(ord(cfg["keys"]["yes"]), ord(cfg["keys"]["no"]))
        )
    return stairs.threshold()


def load_config(config_file):
    with open(config_file) as f:
        cfg = json.load(f)
    return cfg


def main(config_file):
    cfg = load_config(config_file)
    threshold = audiogram(cfg)
    print(f"The hearing threshold at {cfg["frequency"]} Hz is {threshold} dB")


if __name__ == "__main__":
    parser = ArgumentParser()
    parser.add_argument("config_file", type=str)
    args = parser.parse_args()
    main(args.config_file)

```

The `ArgumentParser` takes in the path to our config and passes it to the `main()` function.
In turn, `main()` calls `load_config()` and passes the parameters to `audiogram()` which runs the actual experiment.
While this does the same as our previous code, it allows us to reconfigure the experiment by merely editing `config.json`.
Now, we can run audiograms for different frequencies and durations without ever touching our code!

## Making sure the configuration is valid

While the approach above may seem convenient, it carries large risks.
The program has no knowledge of the stored parameters before they are accessed the first time.
This means that the program may start despite an invalid parameters and then crash in the middle of the experiment when that parameter is first accessed.
To avoid this, we could add a function that validates our configuration after it has been loaded, for example:

```python
   def load_config(config_file):
    with open(config_file) as f:
        cfg = json.load(f)
    return validate_config(cfg)


def validate_config(cfg):
    for key in [
        "frequency",
        "stimulus_duration",
        "ramp_duration",
        "start_val",
        "n_reversals",
        "keys",
    ]:
        assert key in cfg.keys()
    assert isinstance(cfg["stimulus_duration"], float)
    assert isinstance(cfg["ramp_duration"], float)
    # ... more asserts
    return cfg
```

The `validate_config()` function checks if the config contains all required keys and asserts that the duration parameters are floating numbers (slab interprets floating numbers as seconds and integers as samples).
By stacking multiple assert statements we can test all conditions that define a valid config.
However, this quickly makes the code unreadable.
Whats more, the validation function does not fix the opacity issue.
The program still does not know the content of the config before accessing it - if we forget important checks during validation, the experiment may still crash.

## Pydantic to the rescue

Instead of a validation function, we can use a Pydantic model.
A model is defined as a class by inheriting from Pydantic's `BaseModel`.
The model is simply a collection of fields, each with a specific type.

```python
from Pydantic import BaseModel

class Config(BaseModel):
    frequency: int
    stimulus_duration: float
    ramp_duration: float
    start_val: int
    n_reversal: int
    keys: dict
```

Now, after loading the `config.json`, we can simply create an instance of our `Config` model by passing the keyword arguments from the dictionary.
While creating the instance, Pydantic will make sure all parameters are present, check if they have the correct type, try to convert them if they don't and raise an error if conversion is not possible.

```python
def load_config(config_file):
    with open('config.json') as f:
        config = json.load(f)
    return Config(**config) 
```

Now our `audiogram()` function can get it's parameters by accessing the fields of the config model:

```python
def audiogram(cfg: Config) -> float:
    stimulus = slab.Sound.tone(cfg.frequency, cfg.stimulus_duration)
    stimulus = stimulus.ramp(when="both", duration=cfg.ramp_duration)
    stairs = slab.Staircase(cfg.start_val, cfg.n_reversals)
    for level in stairs:
        stimulus.level = level
        stairs.present_tone_trial(
            stimulus, key_codes=(ord(cfg.keys["yes"]), ord(cfg.keys["no"]))
        )
    return stairs.threshold()
```

## Type hinting

You may have noticed the new notation is the function definition above: `def audiogram(cfg:Config) -> float`.
These are type hints indicating that the `audiogram` function takes an argument that is an instance of the `Config` class and returns a floating number.
These type hints allow tools like LSPs [^4] and type-checkers like MyPy [^5] to automatically check that the operations performed on any variable are valid given that variables type.
This enables us to catch logical inconsistencies in our code before they affect the experiment!

## Extended validation

Sometimes, we want to validate our data beyond making sure they are of the correct type.
For example, in the audiogram, we may want to make sure that the toe frequency is within the human hearing range.
For this purpose, Pydantic offers a `field_validator` decorator [^6] that allows us to define validation functions that are automatically executed when a value is assigned to a specific field of the model.
Below, we add a validation function that takes in the value assigned to the field `frequency` and makes sure it lies within the human hearing range.


```python
class Config(BaseModel):
    frequency: int
    # other fields 
    
    @field_validator("frequency")
    @staticmethod
    def frequency_is_audible(value):
        assert 20 <= value <= 20000
        return value
```

You may have noticed that the `keys` field in the `Config` model is a dictionary.
This creates the same problem we had in the beginning, namely that the content of the dictionary can not be validated before it is accessed.
To overcome this, we can create another Pydantic model called `Keys` and require that the `keys` parameter in the `Config` model is an instance of that class.

```python

class Config(BaseModel):
    # other fields
    keys: Keys

class Keys(BaseModel):
    yes: str
    no: str
    
    @field_validator("yes", "no")
    @staticmethod
    def is_single_digit(value):
        assert len(value)==1
        return value
```

By nesting models within models, we can create detailed validation schemes that can handle even the most complex data!

## Closing remarks

In this post, we explored how to use Pydantic and type hints to create more robust experiments.
You may wonder if all of this is necessary - after all, this was a rather simple example.
However, the example was deliberately simplified to fit within the scope of a blog post and omitted key parts of the experiments such as writing response data.
The more complex an experiment becomes, the more opportunities for errors there are.
This is where type hinting can really shine.
By using type hints and validation, we can make it impossible to represent states that our program can't handle.
This way, we don't have to be mindful of all the parameters and operations carried out on them, our program will do it for us!

There is also no requirement to type hint and validate every last parameter of your experiment.
In our example, we may just define the `Config` class, without any additional validator functions or nested models, and add a single type hint to the `audiogram` function.
This is very little effort and substantially improves the robustness of the program.
However, the tools demonstrated here also allow the definition of detailed validation schemes that can handle even the most complex data - it is your choice how to use them!

If you are interested in exploring the topics introduced here further, I can recommend checking out [Pydantic's documentatio](https://docs.pydantic.dev/latest/) as well as the book [Robust Python by Patrick Viafore](https://www.oreilly.com/library/view/robust-python/9781098100650/).
Finally, here is the code for the complete type-hinted and validated experiment:

```python
``from argparse import ArgumentParser
import json
import slab
from pydantic import BaseModel, field_validator


class Keys(BaseModel):
    yes: str
    no: str

    @field_validator("yes", "no")
    @staticmethod
    def is_single_digit(value):
        assert len(value) == 1
        return value


class Config(BaseModel):
    frequency: int
    stimulus_duration: float
    ramp_duration: float
    start_val: int
    n_reversals: int
    keys: Keys

    @field_validator("frequency")
    @staticmethod
    def frequency_is_audible(value):
        assert 20 <= value <= 20000
        return value


def audiogram(cfg: Config) -> float:
    stimulus = slab.Sound.tone(cfg.frequency, cfg.stimulus_duration)
    stimulus = stimulus.ramp(when="both", duration=cfg.ramp_duration)
    stairs = slab.Staircase(cfg.start_val, cfg.n_reversals)
    for level in stairs:
        stimulus.level = level
        stairs.present_tone_trial(
            stimulus, key_codes=(ord(cfg.keys.yes), ord(cfg.keys.no))
        )
    return stairs.threshold()


def load_config(config_file: str) -> Config:
    with open(config_file) as f:
        config = json.load(f)
    return Config(**config)


def main(config_file: str):
    config = load_config(config_file)
    threshold = audiogram(config)
    print(f"The hearing threshold at {config.frequency} Hz is {threshold} dB")


if __name__ == "__main__":
    parser = ArgumentParser()
    parser.add_argument("config_file", type=str)
    args = parser.parse_args()
    main(args.config_file)
```

## Footnotes
[^1]: Schönwiesner, M., & Bialas, O. (2021). s (ound) lab: An easy to learn Python package for designing and running psychoacoustic experiments. Journal of Open Source Software, 6(62), 3284.
[^2]: If the setup is not calibrated, the hearing threshold will represent the absolute sound level but the intensity relative to other sounds.
[^3]: JSON stands for "JavaScript Object Notation" which is a widely used file standard.
[^4]: LSP stands for "Language Server Protocol" which is a program that runs in the background and provides your code editor with features like syntax highlighting and code completion.
[^5]: While MyPy is not covered in this post, it is a power tool for automated type checking, see the [online documentation](https://mypy-lang.org/)
[^6]: In a nutshell, a decorator is a function that modifies the execution of another function. For more detail, see [this post](https://realpython.com/primer-on-python-decorators/)
