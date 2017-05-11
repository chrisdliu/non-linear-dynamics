Controls:

    Left click to press buttons.

    Clicking a field will highlight it to be edited. Press enter when done.
        Green: Valid
        Blue: Invalid (out of range)
        Red: Can't parse

        You can enter large numbers in number fields by using exponents.
            ex: 2^40, 3^17

    Arrow keys to move around the world.
    IJKL to move around faster.
    Current CX and CY are the coordinates of the center cell of the screen.
    Pressing 'move' will move the current coordinates to the coordinates in the CX and CY fields.
    A: Zoom out
    S: Zoom in
    T: Tick once

    Maximum viewing range: -2^62 to 2^62-1 (I think)
    NOTE: Once the world size exceeds 2^63, you won't be able to see the world anymore.

How to use:

    Change the rule if you want to.
        You won't be able to change the rule after initializing.
        The default rule is the Game of Life: 'B3/S23'
        Rule format (regular expression):
            'B[1-8]{1,8}/S[0-8]{1-9}'
            The numbers after 'B' are the neighbor counts for which a new cell is born.
                Zero is not allowed for obvious reasons.
            The numbers after 'S' are the neighbor counts for which a living cell survives.

        CAUTION:
            It is not advised to immediately run a large number of generations when changing the rule.
            The hashlife algorithm performs well on repeating patterns, which the Game of Life exhibits.
            If the new rule is chaotic, the algorithm will exponentially slower.

    Press 'initialize' to set up the world.

    Now you can click on the screen to toggle cells.

    Once you have set your initial state, press 'start'.
        You won't be able to change cells when running.

    Pressing 'tick' (or pressing 't' on the keyboard) will advance the world by n generations
        n = gen speed
        Max n: 2^62 (not sure why 2^63 doesn't work)

    Pressing 'run' will advance the world by n generations m times per second
        n = gen speed
        m = tick speed

    Press 'stop' to stop advancing.

    When you are finished with the current world, press 'end'.

    Start again from the top.
