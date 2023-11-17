with open('generatedcodeVLOG.txt', 'w') as f:
    f.write('case (schakelaar_dec)\n\t')
    for i in range(50):
        s = i*2
        f.write(f'{i}: begin\n\t\t')
        f.write(f'iopin[{s}] =  M_signalSel_q[0];\n\t\t')
        f.write(f'iopin[{s+1}] =  M_signalSel_q[1];\n\t\t')
        f.write('end\n\t')
    f.write('endcase')

        