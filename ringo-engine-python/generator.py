import sys

def parse_flags(flags):
    flags = flags.split(',')
    parsed = {}
    for f in flags:
        split = f.split('=')
        parsed[split[0].strip()] = split[1].strip() == 'True'
    return parsed


if len(sys.argv) != 3:
    print "Invalid syntax, should be %s [input] [output]" % sys.argv[0]
    sys.exit()

method_names = {}

with open(sys.argv[1], 'r') as in_file:
    with open(sys.argv[2], 'w') as out_file:
        for line in in_file.readlines():
            print line
            if line[0] == '#':
                continue
            args = [j for j in line.split('\t') if len(j.strip())>0]
            method = args[0]
            if method in method_names:
                method_names[method] += 1
                method += str(method_names[method])
            else:
                method_names[method] = 1

            provenance = parse_flags(args[1])['provenance']
            out = "\t@registerOp('%s'" % method
            if not provenance:
                out += ', False'
            out += ')\n'

            snap_args = []
            ringo_in = ['self']
            snap_obj = set()
            ringo_out = []
            ret = ''

            method_prefix = ''
            method_postfix = []
            lineage = []

            for param in args[2:]:
                info = [p.strip() for p in param.split(',')]
                name = info[0]

                if info[3] == 'Y':
                    snap_obj.add(name)
                elif info[3] != 'N':
                    print info[3], info[3]=='N', info[3] != 'N'
                    raise AttributeError("Invalid argument info %s" % info[3])

                arg_format = 'snap.TBool(%s)' if info[1]=='bool' else '%s'
                snap_args.append(arg_format % info[0])
                input = output = False
                if info[2] == 'I':
                    input = True
                elif info[2] == 'O':
                    output = True
                elif info[2] == 'IO':
                    input = output = True
                elif info[2] == 'R':
                    snap_args.pop()
                    ret = name + ' = '
                    ringo_out.append(name if name not in snap_obj else 'RingoObject(%sId, self)' % name)
                    if name in snap_obj:
                        method_postfix.append('\t\t%sId = self.__UpdateObjects(%s, %s)\n' % (name, name, '%s'))
                else:
                    raise AttributeError("Invalid argument info %s" % info[2])

                if input:
                    ringo_in.append(name if name not in snap_obj else '%sId' % name)
                    if len(info) > 4:
                        ringo_in[-1] += ' = %s' % info[4]
                    if name in snap_obj:
                        method_prefix += '\t\t%s = self.Objects[%s]\n' % (name, name+'Id')
                        lineage.append('self.Lineage[%sId]' % name)
                if output:
                    ringo_out.append(name if name not in snap_obj else 'RingoObject(%sId, self)' % name)
                    if not input and name in snap_obj:
                        method_prefix += '\t\t%s = snap.%s()\n' % (name, info[1])
                        method_postfix.append('\t\t%sId = self.__UpdateObjects(%s, %s)\n' % (name, name, '%s'))

            out += '\tdef %s(%s):\n' % (method, str.join(', ', ringo_in))
            out += method_prefix
            out += '\t\t%ssnap.%s(%s)\n' % (ret, args[0], str.join(', ', snap_args))

            lineage = str.join(' + ', lineage)
            if len(lineage) == 0:
                lineage = "[]"
            for l in method_postfix:
                out += l % lineage

            if len(ringo_out) > 1:
                out += '\t\treturn (%s)\n' % (str.join(', ', ringo_out))
            elif len(ringo_out)>0:
                out += '\t\treturn %s\n' % ringo_out[0]

            out_file.write(out.replace('\t', '    ') + '\n')
