; Copyright (c) 2026 iiPython

; Not perfect, but gives a decent speed rating in Hz.
; Although that "Hertz" value should be interpreted as more of a
; generic benchmark score then a true to god CPU speed measurement.

; R5 - Bench count
; R6 - Total score
; R7 - Lowest score
; R8 - Maximum score

preload:
    .dots     "... "
    .minimum  "Minimum score: \033[32m"
    .average  "Average score: \033[32m"
    .maximum  "Maximum score: \033[32m"
    .hertz    " Hz\033[0m\n"
    .benching "Benchmarking... (fifteen runs)\n\n"

terminate:
    hlt

loop:
    inc r1
    lwa r2, D_READ_ELAPSED
    ldi r3, 1000
    cmp r2, r3
    jlt skip_loop
    ret
    skip_loop:
    jmp loop

bench:
    ldi r1, 0             ; Current amount of executions
    swa r1, D_ZERO_CLOCK  ; Reset elapsed clock
    cal loop

    ; R1 now stores score
    cmp r1, r7
    jge skip_set_minimum
    mov r7, r1
    skip_set_minimum:

    cmp r1, r8
    jle skip_set_maximum
    mov r8, r1
    skip_set_maximum:

    ; Add to total
    add r6, r1

    ; Print score
    swa r1, D_WRITE_INT

    ; Go again if needed
    inc r5
    ldi r1, 15
    cmp r5, r1
    jge skip_bench

    ; Add ... if we're not the last test
    ldi r1, &dots
    swa r1, D_WRITE_STR

    ; Repeat
    jmp bench

    ; If we've done all 15, then return
    skip_bench:
    ret

scoring:
    ldi r1, 10
    swa r1, D_WRITE_CHR

    div r6, r5

    ldi r1, 10
    swa r1, D_WRITE_CHR

    ; Show scores
    ldi r1, &minimum
    swa r1, D_WRITE_STR
    swa r7, D_WRITE_INT
    ldi r1, &hertz
    swa r1, D_WRITE_STR

    ldi r1, &average
    swa r1, D_WRITE_STR
    swa r6, D_WRITE_INT
    ldi r1, &hertz
    swa r1, D_WRITE_STR

    ldi r1, &maximum
    swa r1, D_WRITE_STR
    swa r8, D_WRITE_INT
    ldi r1, &hertz
    swa r1, D_WRITE_STR

    hlt

main:

    ; Set time unit to MILLISECONDS
    ldi r1, 0
    swa r1, D_SET_TIME_UNIT

    ; Initialize minimum/avg/maximum
    ldi r7, 65535
    ldi r8, 0
    ldi r8, 0

    ; Begin benching
    ldi r1, &benching
    swa r1, D_WRITE_STR

    ldi r5, 0
    cal bench

    ; Show scores
    cal scoring

