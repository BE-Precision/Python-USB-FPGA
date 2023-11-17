with open('generatedcode.txt', 'w') as f:
    for i in range(50):
        s = i*2
        f.write(f'else if (schakelaar.q == {i}){{')
        f.write('\n\t')
        f.write(f'if (signalSel.q == 0){{iopin[{s}] = 0; iopin[{s+1}] = 0;}}')
        f.write('\n\t')
        f.write(f'if (signalSel.q == 1){{iopin[{s}] = 0; iopin[{s+1}] = 1;}}')
        f.write('\n\t')
        f.write(f'if (signalSel.q == 2){{iopin[{s}] = 1; iopin[{s+1}] = 0;}}')
        f.write('\n\t')
        f.write(f'if (signalSel.q == 3){{iopin[{s}] = 1; iopin[{s+1}] = 1;}}')
        f.write('\n}\n')
        