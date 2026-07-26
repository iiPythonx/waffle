; Copyright (c) 2026 iiPython

preload:
    .clear      "\033[2J\033[H"
    .return     "\033[2K\r"
    .prompt     "\033[32m$\033[0m "
    .greeting   "\nWelcome to \033[32mNocturne Shell\033[0m!\nCopyright (c) 2026 iiPython\n\n"
    .goodbye    "\n\033[31mGoodbye!\033[0m\n"
    .no_cmd     "\033[32mNocturne\033[0m: no such command exists!\n"
    .version    "\033[32mNocturne Shell\033[0m v0.3.0, powered by \033[34mwaffle\033[0m.\n"
    .help_pre   "Commands: "
    .help_green "\033[32m"
    .help_reset "\033[0m"
    .strftime   "%a %b %-d %H:%M:%S %p %Z %Y\n"
    .mem1       "Probing... "
    .mem2       "\rMemory usage: "
    .mem3       " B / 4096 B ("
    .mem4       "%)\n"
    .reg1       ": "
    .reg2       " | "
    .memdump    "Memory snapshot written to snapshot.bin!\n"

    ; Commands
    .str_version "version"
    .str_help    "help"
    .str_exit    "exit"
    .str_clear   "clear"
    .str_mem     "mem"
    .str_reg     "reg"
    .str_date    "date"
    .str_memdump "memdump"

terminate:
    ldi r1, 10
    swa r1, D_WRITE_CHR
    ldi r1, &goodbye
    swa r1, D_WRITE_STR
    hlt

write:
    ldi r1, &return
    swa r1, D_WRITE_STR

    ; Prompt
    ldi r1, &prompt
    swa r1, D_WRITE_STR

    ; String write
    ldi r1, 0x2400
    swa r1, D_WRITE_STR
    ret

match_command:
    ; R2 = Memory address of string 1
    ; R3 = Memory address of string 2
    lbr r4, r2  ; R4 = String 1 character
    lbr r5, r3  ; R5 = String 2 character

    ; Check if they aren't the same (quick abort)
    cmp r4, r5
    jeq skip_abort

    ; They are in fact not the same, abort now
    ldi r9, 0
    ret

    skip_abort:

    ; They are in fact the same, continue processing
    ldi r5, 0   ; Overwriting r5 is fine now, value used
    cmp r4, r5  ; Check if r4 is zero
    jne skip_abort2

    ; Both characters were the same, and were both zero, so match is good
    ldi r9, 1
    ret

    skip_abort2:

    inc r2
    inc r3
    jmp match_command

run_command:
    mov lc, r4

iterate_command_table:

    ; R1 = Memory address of command table
    lwr r2, r1
    ldi r3, 0x2400

    ; Check for zero (end of table)
    ldi r4, 0
    cmp r2, r4
    jne continue_loop
    ret

    ; Match the command
    continue_loop:
    cal match_command

    ; Add 2 bytes
    inc r1
    inc r1

    lwr r4, r1

    ; If success, run command
    ldi r8, 1
    cmp r9, r8
    jne continue_loop2
    swa r8, 0x2910       ; Mark as valid command
    cal run_command
    ret

    continue_loop2:

    ldi r8, 0
    swa r8, 0x2910       ; Mark as invalid command

    inc r1
    inc r1

    jmp iterate_command_table

cmd_version:
    ldi r1, &version
    swa r1, D_WRITE_STR
    ret

cmd_help_loop:
    ldi r4, &help_green
    swa r4, D_WRITE_STR
    swa r3, D_WRITE_STR
    ldi r4, &help_reset
    swa r4, D_WRITE_STR

    add r1, r2

    lwr r3, r1
    ldi r4, 0
    cmp r3, r4
    jne continue_printing
    ret

    continue_printing:
    ldi r4, ','
    swa r4, D_WRITE_CHR
    ldi r4, ' '
    swa r4, D_WRITE_CHR
    jmp cmd_help_loop

cmd_help:
    ldi r1, &help_pre
    swa r1, D_WRITE_STR

    ldi r1, 0x2800
    ldi r2, 4
    lwr r3, r1
    cal cmd_help_loop

    ; Newline
    ldi r1, 10
    swa r1, D_WRITE_CHR

    ret

cmd_exit:
    ldi r1, &goodbye
    swa r1, D_WRITE_STR
    hlt

cmd_clear:
    ldi r1, &clear
    swa r1, D_WRITE_STR
    ret

cmd_date:
    ldi r1, &strftime
    swa r1, D_SET_TIME_FMT
    ldi r1, 0x2850
    swa r1, D_READ_TIME_FMT
    swa r1, D_WRITE_STR
    ret

print_reg:
    ldi r1, 'R'
    swa r1, D_WRITE_CHR
    swa r2, D_WRITE_CHR
    ldi r1, &reg1
    swa r1, D_WRITE_STR
    lwr r1, r3
    swa r1, D_WRITE_INT
    ldi r1, 57
    cmp r2, r1
    jeq skip_reg_print
    ldi r1, &reg2
    swa r1, D_WRITE_STR
    skip_reg_print:
    ret

reg_loop:
    cal print_reg
    inc r2
    inc r3
    inc r3
    ldi r1, 58
    cmp r2, r1
    jeq skip_reg_jump
    jmp reg_loop
    skip_reg_jump:
    ret

cmd_reg:
    swa r1, 0x2850
    swa r2, 0x2852
    swa r3, 0x2854
    swa r4, 0x2856
    swa r5, 0x2858
    swa r6, 0x285A
    swa r7, 0x285C
    swa r8, 0x285E
    swa r9, 0x2860

    ldi r2, '1'
    ldi r3, 0x2850
    cal reg_loop

    ldi r1, 10
    swa r1, D_WRITE_CHR

    ret

count_mem:

    ; Have we hit the stack?
    ldi r3, 0x3000
    cmp r2, r3
    jeq skip_mem_count     ; If yes, then return

    ; Load byte from DATA
    lbr r3, r2
    ldi r4, 0
    cmp r3, r4             ; Is it NULL? (0)
    jeq skip_byte_count    ; If it is, skip it
    inc r1                 ; If it isn't, increment R1
    skip_byte_count:

    ; Increment DATA pointer
    inc r2

    ; And loop back
    jmp count_mem

    ; Finally, return (once we hit STACK)
    skip_mem_count:
    ret

cmd_mem:
    ldi r1, &mem1
    swa r1, D_WRITE_STR

    ; Starting counters
    ldi r1, 0
    ldi r2, 0x2000
    cal count_mem
    mov r2, r1             ; I love abusing r1, so move to r2

    ; Logging
    ldi r1, &mem2
    swa r1, D_WRITE_STR
    swa r2, D_WRITE_INT
    ldi r1, &mem3
    swa r1, D_WRITE_STR

    ; Percentage
    ldi r1, 100
    mul r2, r1
    ldi r1, 0x1000
    div r2, r1

    swa r2, D_WRITE_INT

    ; Closing
    ldi r1, &mem4
    swa r1, D_WRITE_STR
    ret

cmd_memdump:
    ldi r1, &memdump
    swa r1, D_MEMORY_SNAPSHOT
    swa r1, D_WRITE_STR
    ret

validate_command_status:
    lwa r1, 0x2910
    ldi r7, 1
    cmp r1, r7
    jne no_such_command
    ret

    no_such_command:
    ldi r1, &no_cmd
    swa r1, D_WRITE_STR
    ret

register_command:
    swr r2, r1
    add r1, r4
    swr r3, r1
    add r1, r4
    ret

init_table:
    ldi r1, 0x2800
    ldi r4, 2

    ; version
    ldi r2, &str_version
    ldi r3, cmd_version
    cal register_command

    ; help
    ldi r2, &str_help
    ldi r3, cmd_help
    cal register_command

    ; exit
    ldi r2, &str_exit
    ldi r3, cmd_exit
    cal register_command

    ; clear
    ldi r2, &str_clear
    ldi r3, cmd_clear
    cal register_command

    ; mem
    ldi r2, &str_mem
    ldi r3, cmd_mem
    cal register_command

    ; reg
    ldi r2, &str_reg
    ldi r3, cmd_reg
    cal register_command

    ; date
    ldi r2, &str_date
    ldi r3, cmd_date
    cal register_command

    ; memdump
    ldi r2, &str_memdump
    ldi r3, cmd_memdump
    cal register_command

    ret

execute:

    ; Newline
    ldi r1, 10
    swa r1, D_WRITE_CHR

    ; Check command matches
    ldi r1, 0x2800
    cal iterate_command_table

    ; Check command status
    cal validate_command_status

    ; Reset feed address
    ldi r2, 0x2400
    ldi r1, 0

    ; Mark as zero
    sbr r1, r2
    
    ; Pass back
    ldi r9, 10
    ret

backspace:
    dec r2

    ldi r1, 0
    swr r1, r2

    ; Pass back
    ldi r9, 10
    ret

push:

    ; Append to RAM
    sbr r1, r2

    ; Push back address
    inc r2

    ; Null terminate it (for WRITE_STR)
    ldi r1, 0
    swr r1, r2

    ret

shell:
    cal write

    ; Intake
    lwa r1, D_READ_CHR
    ldi r9, 0

    ; Check for [ENTER]
    ldi r3, 10
    cmp r1, r3
    jne skip_execute
    cal execute
    skip_execute:

    ; Check for [BACKSPACE]
    ldi r3, 127
    cmp r1, r3
    jne skip_backspace
    cal backspace
    skip_backspace:

    ; Everything else
    ldi r3, 10
    cmp r9, r3
    jeq skip_push
    cal push
    skip_push:

    ; Push to terminal
    cal write
    jmp shell

main:
    cal init_table

    ; Greeting
    ldi r1, &clear
    swa r1, D_WRITE_STR

    ldi r1, &greeting
    swa r1, D_WRITE_STR

    ; Feed store
    ldi r2, 0x2400

    ; Loop
    jmp shell
