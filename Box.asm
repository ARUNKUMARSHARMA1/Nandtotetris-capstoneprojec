// Box.asm - K = 76
// Box starts at screen row 76, is 20 rows tall, and is 16 pixels wide.
// Each screen row contains 32 words, so advance 32 words for each vertical step.
// Hold any key to draw the black box; release any key to erase it.

(START)
    @KBD
    D=M
    @DRAW
    D;JGT

// No key pressed: erase the 20 vertical screen words.
(ERASE)
    @SCREEN
    D=A
    @2432
    D=D+A
    @R13
    M=D
    @20
    D=A
    @R14
    M=D
(ERASE_LOOP)
    @R13
    A=M
    M=0
    @32
    D=A
    @R13
    M=D+M
    @R14
    MD=M-1
    @ERASE_LOOP
    D;JGT
    @START
    0;JMP

// Key pressed: draw one 16-pixel-wide black word on each of 20 rows.
(DRAW)
    @SCREEN
    D=A
    @2432
    D=D+A
    @R13
    M=D
    @20
    D=A
    @R14
    M=D
(DRAW_LOOP)
    @R13
    A=M
    M=-1
    @32
    D=A
    @R13
    M=D+M
    @R14
    MD=M-1
    @DRAW_LOOP
    D;JGT
    @START
    0;JMP
