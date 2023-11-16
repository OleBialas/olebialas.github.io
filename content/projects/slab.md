+++
title = 'S(ound)lab: A python package for running psychoacoustic experiments'
date = 2023-11-06T13:29:06-05:00
draft = false
description = 'Slab was designed for creating and running experiments on acoustic perception while providing a good learning experience for users lacking prior experience in coding.'
tags = ['Python', 'science', 'sound', 'signal processing']
cover = 'fbank.png'
+++

## Why slab?
Many researchers who lack formal training in coding turn to software providing graphical user interfaces to select and configure components for their experiment. Unfortunately, this reduces transparency and reproducibility and limits the users understanding and control of the experiment.

Slab addresses this problem by providing researchers with a way to flexibly design their experiments that facilitates learning and understanding of the underlying code and procedures.
Slab is routinely used in behavioral and neurimaging experiments and was published in the academic Journal of Open Source Software [^1].

## Design

Rather than providing ready-made solutions, slab provides basic building blocks, allowing flexible experimental design with clean and maintainable code. These building blocks are implemented in several classes:

- **Signal**: base class for sounds and filters. Typically not directly accessed.
- **Sound** (inherits from Signal): generate simple sounds, like white noise or pure tones, manipulate and play them. 
- **Filter** (inherits from Signal): Create and apply filters (shown in the title title figure), for example to equalize loudspeakers.
- **HRTF** (inherits from Filter): stands for head-related transfer function - a special kind of filter for simulating spatial audio.
- **Trialsequence/Staircase**: generate and iterate trough different experimental sequences and record responses.


## Example

For a demonstration of slab, let's consider the implementation of a pure tone
audiogram which measures the hearing threshold across different frequencies.

In the code below, we generate pure tones with different `frequencies` using the `slab.Sound.tone()` method. Then, we run a `staircase` sequence which determines the level at which the tone is played. The method `staircase.present_tone_trial()` plays the tone, waits for the listeners response (press 1 if you heard it and 2 if you didn't) and adjusts the sound level accordingly. 

The `staircase` will decrease the tone's level until you can't hear it anymore, then increase it until you hear it again, then decrease it again and so on, until a certain number of reversals is reached (here 5). The threshold at a given frequency is then calculated as the mean intensity of all reversal points.

```python
import slab
from matplotlib import pyplot as plt
frequencies = [125, 250, 500, 1000, 2000, 4000]
threshs = []
for frequency in freqs:
    stimulus = slab.Sound.tone(frequency=frequency, duration=0.5)
    staircase = slab.Staircase(start_val=50, n_reversals=5)
    print(f'Starting staircase with {frequency} Hz:')
    for level in staircase:
        stimulus.level = level
        staircase.present_tone_trial(stimulus)
        staircase.print_trial_info()
    threshs.append(staircase.threshold())
    print(f'Threshold at {frequency} Hz: {staircase.threshold()} dB')
plt.plot(freqs, threshs) # plot the audiogram
```

The resulting curve indicates the hearing threshold across frequencies. Note that, since the setup is not calibrated, these thresholds can not be interpreted in absolute terms, but only relative to each other. The curve's minimum should be between 2 and 4 kHz, where the human ear is most sensitive, coinciding with the main frequency range of speech.

![audiogram plots](/audiogram.png)

## Further reading

If you are interested in learning more about slab you should check out the projects 
[online documentation](https://slab.readthedocs.io/en/latest/index.html), which provides detailed tutorials and examples for the different 
functionalities of the toolbox.

## References

[^1]:Schönwiesner, M., & Bialas, O. (2021). s(ound) lab: An easy to learn Python package for designing and running psychoacoustic experiments. Journal of Open Source Software, 6(62), 3284.
