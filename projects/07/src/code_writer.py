"""
A register: 데이터 레지스터와 주소 레지스터
D register: 데이터 값
M: 메모리
"""
import os, os.path
from vm_constant import *


class CodeWriter:
    def __init__(self, filepath: str) -> None:
        self.output_file = open(filepath, "w")
        self._n_label = 0
        self._com2asm = {
            # binary
            "add": ("D+A", "b"),
            "sub": ("A-D", "b"),
            "and": ("A&D", "b"),
            "or": ("A|D", "b"),

            # uni
            "not": ("!D", "u"),
            "neg": ("-D", "u"),

            # compare
            "eq": ("JEQ", "c"),
            "gt": ("JGT", "c"),
            "lt": ("JLT", "c"),
        }

    def write_init(self):
        # SP
        self._write_a_command("256")
        self._write_c_command(
            dest="D",
            comp="A",
        )
        self._comp_to_reg(
            regnum=R_SP, comp="D",
        )

        # Local
        self._write_a_command("300")
        self._write_c_command(
            dest="D",
            comp="A",
        )
        self._comp_to_reg(
            regnum=R_LCL, comp="D",
        )

        # ARG
        self._write_a_command("400")
        self._write_c_command(
            dest="D",
            comp="A",
        )
        self._comp_to_reg(
            regnum=R_ARG, comp="D",
        )

        # This 
        self._write_a_command("3000")
        self._write_c_command(
            dest="D",
            comp="A",
        )
        self._comp_to_reg(
            regnum=R_THIS, comp="D",
        )

        # That
        self._write_a_command("3010")
        self._write_c_command(
            dest="D",
            comp="A",
        )
        self._comp_to_reg(
            regnum=R_THAT, comp="D",
        )

        # Temp
        self._write_a_command("5")
        self._write_c_command(
            dest="D",
            comp="A",
        )
        self._comp_to_reg(
            regnum=R_TEMP, comp="D",
        )


        # self.write_call("Sys.init", 0)

    def writeGoto(self, label: str) -> None:
        self._write_a_command(address=label)
        self._write_c_command(dest=None, comp="0", jump="JMP")

    def writeIf(self, label: str) -> None:
        self._pop_to_dest("D")
        self._write_a_command(address="label")
        self._write_c_command(dest=None, comp="D", jump="JNE")

    def _pop_to_dest(self, dest: str) -> None:
        self._dec_sp()
        self._stack_to_dest(dest=dest)

    def writeLabel(self, label: str) -> None:
        self._write_l_command(label=label)

    def writeFunction(self, function_name: str, num_locals: int) -> None:
        self._write_l_command(function_name)
        for i in range(num_locals):
            self._write_push(segment=S_CONST, index=0)

    def writeReturn(self) -> None:
        self._reg_to_reg(dest=R_FRAME, src=R_LCL)
        self._write_a_command("5")
        self._write_c_command(dest="A", comp="D-A")
        self._write_c_command(dest="D", comp="M")
        self._comp_to_reg(regnum=R_RET, comp="D")
        self._write_pop(segment=S_ARG, index=0)
        self._reg_to_dest(dest="D", regnum=R_ARG)
        self._comp_to_reg(regnum=R_SP, comp="D+1")
        self._prev_frame_to_reg(R_THAT)
        self._prev_frame_to_reg(R_THIS)
        self._prev_frame_to_reg(R_ARG)
        self._prev_frame_to_reg(R_LCL)
        self._reg_to_dest(dest="A", regnum=R_RET)
        self._write_c_command(dest=None, comp="0", jump="JMP")

    def _prev_frame_to_reg(self, regnum: int) -> None:
        self._reg_to_dest(dest="D", regnum=R_FRAME)
        self._write_c_command(dest="D", comp="D-1")
        self._comp_to_reg(regnum=R_FRAME, comp="D")
        self._write_c_command(dest="A", comp="D")
        self._write_c_command(dest="D", comp="M")
        self._comp_to_reg(regnum=regnum, comp="D")
        

    def writeCall(self, function_name: str, num_args: int) -> None:
        return_address = self._create_new_label()
        self._write_push(S_CONST, return_address) # push return_address
        self._write_push(S_REG, R_LCL)            # push LCL
        self._write_push(S_REG, R_ARG)            # push ARG
        self._write_push(S_REG, R_THIS)           # push THIS
        self._write_push(S_REG, R_THAT)           # push THAT
        self._load_sp_offset(-num_args-5)
        self._comp_to_reg(R_ARG, 'D')       # ARG=SP-n-5
        self._reg_to_reg(R_LCL, R_SP)       # LCL=SP
        self._write_a_command(function_name)      # A=function_name
        self._write_c_command(None, '0', 'JMP')   # 0;JMP
        self._write_l_command(return_address)     # (return_address)

    def _load_sp_offset(self, offset: int) -> None:
        self._load_seg(self._asm_reg(R_SP), offset)

    def _reg_to_reg(self, dest: str, src: str) -> None:
        self._reg_to_dest('D', src)
        self._comp_to_reg(dest, 'D')        # Rdest = Rsrc
        
    def setFileName(self, filename: str) -> None:
        pass

    def close(self):
        self.output_file.close()

    def writeArithmetic(self, command: str) -> None:
        asm, type = self._com2asm[command]
        if type == "b":
            self._binary(asm)
        elif type == "c":
            self._compare(asm)
        elif type == "u":
            self._uniary(asm)

    def _load_sp(self):
        """_load_sp
        A register에 SP(stack point) load
        A=&SP
        A=SP
        """
        self._write_a_command("SP")
        self._write_c_command(
            dest="A",
            comp="M",
        )

    def _stack_to_dest(self, dest: str):
        """_stack_to_dest
        dest=*SP
        """
        self._load_sp()
        self._write_c_command(
            dest=dest,
            comp="M",
        )

    def _inc_sp(self):
        """
        stack point 증가
        A=&SP
        SP=SP-1
        """
        self._write_a_command("SP")
        self._write_c_command(
            dest="M",
            comp="M+1",
        )

    def _dec_sp(self):
        """
        stack point 감소
        A=&SP
        SP=SP-1
        """
        self._write_a_command("SP")
        self._write_c_command(
            dest="M",
            comp="M-1",
        )

    def _comp_to_stack(self, comp: str):
        """_comp_to_stack
        A=&SP
        M=comp
        """
        self._load_sp()
        self._write_c_command(
            dest="M",
            comp=comp,
        )

    def _uniary(self, comp: str):
        """
        
        """
        self._dec_sp()
        self._stack_to_dest(dest="D")
        self._write_c_command(
            dest="D",
            comp=comp,
        )
        self._comp_to_stack(comp="D")
        self._inc_sp()

    def _binary(self, comp: str):
        """AI is creating summary for _binary

        Args:
            comp (str): [description]
        """
        self._dec_sp()
        self._stack_to_dest(dest="D")
        self._dec_sp()
        self._stack_to_dest(dest="A")
        self._write_c_command(
            dest="D",
            comp=comp,
        )
        self._comp_to_stack(comp="D")
        self._inc_sp()

    def _compare(self, jump: str):
        """AI is creating summary for _compare

        Args:
            comp (str): [description]
        """
        self._dec_sp()
        self._stack_to_dest(dest="D")
        self._dec_sp()
        self._stack_to_dest(dest="A")
        self._write_c_command(
            dest="D",
            comp="A-D",
        )
        eq_label = self._jump(comp="D", jump=jump)
        self._comp_to_stack(comp="0")
        neq_label = self._jump(comp="0",jump="JMP")
        self._write_l_command(label=eq_label)
        self._comp_to_stack("-1")
        self._write_l_command(label=neq_label)
        self._inc_sp()

    def _jump(self, comp: str, jump: str) -> str:
        label = self._create_new_label()
        self._write_a_command(address=label)
        self._write_c_command(
            dest=None,
            comp=comp,
            jump=jump,
        )
        return label
    

    def _create_new_label(self) -> str:
        self._n_label += 1
        return "LABEL" + str(self._n_label)

    def _write_a_command(self, address: str):
        self.output_file.write("@" + address + "\n")
        
    def _write_c_command(
        self,
        dest: str = None,
        comp: str = None,
        jump: str = None,
    ):
        """C Command 
        i) dest is None: ex) 0;JGT
        ii) jump is None ex) D=D-A
        Args:
            dest (str): [description]
            comp (str): [description]
            jump (str): [description]
        """
        if dest:
            self.output_file.write(dest + "=")
        self.output_file.write(comp)
        if jump:
            self.output_file.write(";" + jump)
        self.output_file.write("\n")

    def _write_l_command(self, label: str) -> None:
        self.output_file.write(f"({label})\n")

    def writePushPop(
        self,
        command: str,
        segment: str,
        index: int
    ) -> None:
        if command == C_PUSH:
            return self._write_push(segment=segment, index=index)
        elif command == C_POP:
            return self._write_pop(segment=segment, index=index)

    def _write_push(self, segment: str, index: int) -> None:
        if self._is_const_seg(segment):
            self._val_to_stack(str(index))
        elif self._is_mem_seg(segment):
            self._mem_to_stack(segment=self._asm_mem_seg(segment), index=index)
        elif self._is_reg_seg(segment):
            self._reg_to_stack(segment=segment, index=index)
        elif self._is_static_seg(segment):
            self._static_to_stack(segment=segment, index=index)
        self._inc_sp()

    def _write_pop(self, segment: str, index: int) -> None:
        self._dec_sp()
        if self._is_mem_seg(segment):
            self._stack_to_mem(segment=self._asm_mem_seg(segment), index=index)
        elif self._is_reg_seg(segment):
            self._stack_to_reg(segment=segment, index=index)
        elif self._is_static_seg(segment):
            self._stack_to_static(segment=segment, index=index)

    # Types of segments

    def _is_mem_seg(self, seg: str) -> bool:
        return seg in [S_LCL, S_ARG, S_THIS, S_THAT]
        
    def _is_reg_seg(self, seg: str) -> bool:
        return seg in [S_REG, S_PTR, S_TEMP]

    def _is_static_seg(self, seg: str) -> bool:
        return seg == S_STATIC

    def _is_const_seg(self, seg: str) -> bool:
        return seg == S_CONST

    def _val_to_stack(self, val: str):
        self._write_a_command(address=val)
        self._write_c_command(dest="D", comp="A")
        self._comp_to_stack(comp="D")

    def _mem_to_stack(self, segment: str, index: int, indir: bool = True):
        self._load_seg(segment=segment, index=index, indir=indir)
        self._write_c_command(dest="D", comp="M")
        self._comp_to_stack(comp="D")

    def _stack_to_mem(self, segment: str, index: int, indir: bool = True):
        self._load_seg(segment=segment, index=index, indir=indir)
        self._comp_to_reg(R_COPY, 'D')              
        self._stack_to_dest(dest='D') 
        self._reg_to_dest(dest='A', regnum=R_COPY)     
        self._write_c_command(dest='M', comp='D')

    def _stack_to_reg(self, segment: str, index: int):
        self._stack_to_dest('D')            # D=*SP
        self._comp_to_reg(regnum=self._reg_num(segment=segment, index=index), comp='D')

    def _comp_to_reg(self, regnum: int, comp: str):
        self._write_a_command(self._asm_reg(regnum)) # @R#
        self._write_c_command(dest='M', comp=comp) 

    def _load_seg(self, segment: str, index: int, indir: bool = True):
        if index == 0:
            self._load_seg_with_no_index(segment=segment, indir=indir)
        else:
            self._load_seg_with_index(segment=segment, index=index, indir=indir)

    def _load_seg_with_no_index(self, segment: str, indir: bool):
        self._write_a_command(address=segment)
        if indir:
            self._indir(dest="AD")

    def _indir(self, dest: str = "A") -> None:
        self._write_c_command(dest=dest, comp="M")

    def _load_seg_with_index(self, segment: str, index: int, indir: bool) -> None:
        comp = "D+A"
        if index < 0:
            index = -index
            comp = "A-D"
        self._write_a_command(address=str(index))
        self._write_c_command(dest="D", comp="A")
        self._write_a_command(address=segment)
        if indir:
            self._indir(dest="A")
        self._write_c_command(
            dest="AD",
            comp=comp,
        )

    def _reg_to_stack(self, segment: str, index: int) -> None:
        self._reg_to_dest(dest="D", regnum=self._reg_num(segment=segment, index=index))
        self._comp_to_stack(comp="D")
    
    def _reg_num(self, segment: str, index: int) -> str:
        return self._reg_base(segment)+index

    def _reg_base(self, segment: str) -> str:
        reg_base = {'reg':R_R0, 'pointer':R_PTR, 'temp':R_TEMP}
        return reg_base[segment]

    def _reg_to_dest(self, dest: str, regnum: int):
        self._write_a_command(self._asm_reg(regnum))
        self._write_c_command(dest=dest, comp="M")

    def _asm_reg(self, regnum: int) -> str:
        return "R" + str(regnum)

    def _asm_mem_seg(self, segment: str):
        asm_label = {S_LCL:'LCL', S_ARG:'ARG', S_THIS:'THIS', S_THAT:'THAT', S_TEMP: 'TEMP'}
        return asm_label[segment]

    def _static_to_stack(self, segment: str, index: int) -> None:
        self._write_a_command(address=self._static_name(index))
        self._write_c_command(dest="D", comp="M")
        self._comp_to_stack(comp="D")

    def _stack_to_static(self, segment: str, index: int) -> None:
        self._stack_to_dest(dest="D")
        self._write_a_command(self._static_name(index))
        self._write_c_command(dest="M", comp="D")

    def _static_name(self, index: int) -> str:
        return "static" + str(index)

