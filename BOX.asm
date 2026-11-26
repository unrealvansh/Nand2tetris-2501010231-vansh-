
(LOOP)
    @KBD
    D=M
    @BLACK
    D;JGT

    // Key released: white
    @COLOR
    M=0
    @DRAW
    0;JMP

(BLACK)
    // Key pressed: black
    @COLOR
    M=-1

(DRAW)
    // Starting row 56
    @18176
    D=A
    @ADDR
    M=D

    // 20 rows
    @20
    D=A
    @ROWS
    M=D

(ROWLOOP)
    @COLOR
    D=M
    @ADDR
    A=M
    M=D

    @32
    D=A
    @ADDR
    M=D+M

    @ROWS
    MD=M-1
    @ROWLOOP
    D;JGT

    @LOOP
    0;JMP
