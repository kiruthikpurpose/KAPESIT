section .data
    state dd 0.707106781, 0.707106781, 0.707106781, -0.707106781
    bell dd 1.0, 0.0, 0.0, 1.0
    
section .bss
    result resd 4
    temp resd 4

section .text
global _start

_start:
    ; Initialize state
    mov eax, state
    call normalize_state
    
    ; Create Bell state
    mov eax, bell
    call create_bell
    
    ; Teleport qubit
    mov eax, state
    mov ebx, bell
    call teleport_qubit
    
    ; Measure final state
    mov eax, result
    call measure_state
    
    ; Exit
    mov eax, 60
    xor edi, edi
    syscall

normalize_state:
    mov ecx, 4
    mov esi, state
    fldz
    loop_norm:
        fld dword [esi]
        fmul st0, st0
        fadd st1, st0
        fstp st0
        add esi, 4
        loop loop_norm
    
    fsqrt
    mov esi, state
    loop_normalize:
        fld dword [esi]
        fdiv st0, st1
        fstp dword [esi]
        add esi, 4
        loop loop_normalize
    ret

create_bell:
    mov ecx, 4
    mov esi, bell
    fldz
    loop_bell:
        fld dword [esi]
        fmul st0, st0
        fadd st1, st0
        fstp st0
        add esi, 4
        loop loop_bell
    
    fsqrt
    mov esi, bell
    loop_bell_normalize:
        fld dword [esi]
        fdiv st0, st1
        fstp dword [esi]
        add esi, 4
        loop loop_bell_normalize
    ret

teleport_qubit:
    ; Apply CNOT
    mov ecx, 4
    mov esi, state
    mov edi, temp
    loop_cnot:
        push ecx
        mov ecx, 4
        mov ebx, bell
        fldz
        loop_row:
            fld dword [ebx]
            fld dword [esi]
            fmul st0, st1
            fadd st2, st0
            fstp st0
            fstp st0
            add ebx, 4
            loop loop_row
        fstp dword [edi]
        add esi, 4
        add edi, 4
        pop ecx
        loop loop_cnot
    ret

measure_state:
    mov ecx, 4
    mov esi, state
    loop_measure:
        fld dword [esi]
        fmul st0, st0
        fcomi st0, st1
        ja collapse
        add esi, 4
        loop loop_measure
    ret

collapse:
    mov eax, 1
    mov ebx, 0
    int 0x80
    ret
