section .data
    state dd 0.0, 0.0, 0.0, 0.0    ; 2-qubit state
    gate dd 0.5, 0.5, 0.5, 0.5      ; Quantum gate
    
section .bss
    result resd 4                    ; Result buffer

section .text
global _start

_start:
    ; Initialize state
    mov eax, 1
    mov ebx, state
    call initialize_state
    
    ; Apply quantum gate
    mov eax, state
    mov ebx, gate
    call apply_gate
    
    ; Measure state
    mov eax, result
    call measure_state
    
    ; Exit
    mov eax, 60
    xor edi, edi
    syscall

initialize_state:
    ; Normalize state vector
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

apply_gate:
    ; Matrix multiplication
    mov ecx, 4
    mov esi, state
    mov edi, result
    loop_gate:
        push ecx
        mov ecx, 4
        mov ebx, gate
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
        loop loop_gate
    ret

measure_state:
    ; Measure quantum state
    mov ecx, 4
    mov esi, result
    loop_measure:
        fld dword [esi]
        fmul st0, st0
        fcomi st0, st1
        ja collapse
        add esi, 4
        loop loop_measure
    ret

collapse:
    ; Collapse state
    mov eax, 1
    mov ebx, 0
    int 0x80
    ret
