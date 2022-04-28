from decimal import Decimal
import os
from math import floor
import time

Decimal_Number = 512
p0_len = 16
block_size = 256

'''
    my long decimal : a integer T with Decimal_Number bit, present a float T >> Decimal_Number.
'''


#  change float p to long decimal dp
def change(p):
    res = 0
    for i in range(p0_len):
        res <<= 1
        p *= 2
        if p >= 1:
            p -= 1
            res |= 1
    return res


#  multiply of long decimal
def decimal_mul(a, b):
    return (a * b) >> Decimal_Number


def LB_encode(ifn):
    #  input
    input_file = open(ifn, 'rb')
    output_file = open(ifn + '.LB', 'wb')

    #  get file size
    file_size = os.path.getsize(ifn)
    sum_size = 0

    #  get present time
    start = time.perf_counter()

    while 1:
        #  UI: progress bar
        nt = sum_size / file_size * 100
        print('\rprocessing:[{}] {:.2f}% '.format(('*' * (floor(nt) // 2)) + ('-' * (50 - floor(nt) // 2)), nt), end='')
        print('({}B / {}B)'.format(sum_size, file_size), end='')
        sum_size += block_size

        #  input a block and check for end
        in_buf = input_file.read(block_size)
        if in_buf == b'':
            break
        ou_buf = bytearray()

        #  count p0, change to decimal and output dp to each block head
        cnt0 = 0
        cnt1 = 0
        for x in in_buf:
            for j in range(8):
                if (x >> j) & 1:
                    cnt1 += 1
                else:
                    cnt0 += 1
        p0 = Decimal(cnt0) / Decimal(cnt0 + cnt1)
        dp = change(p0) << (Decimal_Number - p0_len)
        for i in range(0, p0_len, 8):
            ou_buf.append((dp >> (Decimal_Number - 8 - i)) & 255)

        #  extreme condition: just output length
        if dp == 0 or dp >> (Decimal_Number - p0_len) == ((1 << p0_len) - 1):
            res = len(in_buf)
            while res > 0:
                ou_buf.append(res & 255)
                res >>= 8

        #  common condition
        #  dp1 : probability of 1.  px : probability of hole block.  lx : length of final p(x).
        #  tmp : a register to store output byte.  ll : length of bit in tmp. in [0, 8)
        else:
            '''
                [l, r]
                mid = l + (r - l) * p0
            '''
            tmp = 0
            ll = 0
            dl = 0
            dr = (1 << Decimal_Number) - 1
            px = (1 << Decimal_Number) - 1
            dp1 = px - dp + 1
            lx = 0
            for x in in_buf:
                for i in range(8):
                    dm = dl + decimal_mul(dp, dr - dl)
                    #  print('dl{:77d} dr{:77d} dm{:77d}'.format(dl, dr, dm))
                    if (x >> (7 - i)) & 1:
                        #  choose right
                        dl = dm
                        px = decimal_mul(px, dp1)
                    else:
                        #  choose left
                        dr = dm
                        px = decimal_mul(px, dp)
                    while (px >> (Decimal_Number - 1)) == 0:
                        lx += 1
                        px <<= 1

                    #  print(dl, dr, dm)
                    #  output dl, dr equal prefix
                    while (dl >> (Decimal_Number - 1)) == (dr >> (Decimal_Number - 1)):
                        if dl == dr:
                            print('error')
                            exit(0)
                        lx -= 1
                        if dl >> (Decimal_Number - 1) == 0:
                            dl <<= 1
                            dr <<= 1
                            tmp = tmp << 1
                            ll += 1
                            if ll == 8:
                                ou_buf.append(tmp)
                                ll = 0
                                tmp = 0
                        else:
                            dl -= 1 << (Decimal_Number - 1)
                            dr -= 1 << (Decimal_Number - 1)
                            dl <<= 1
                            dr <<= 1
                            tmp = tmp << 1 | 1
                            ll += 1
                            if ll == 8:
                                ou_buf.append(tmp)
                                ll = 0
                                tmp = 0
            dm = dl + decimal_mul(dp, dr - dl)
            #  print(dm, min(block_size, max(0, lx + 64)))
            #  output decimal to lx + 32 bytes QAQ
            for i in range(min(Decimal_Number, max(0, lx + 32))):
                tmp = tmp << 1
                if (dm >> (Decimal_Number - i - 1)) & 1:
                    tmp |= 1
                ll += 1
                if ll == 8:
                    ou_buf.append(tmp)
                    ll = 0
                    tmp = 0

            #  output remaining bits
            ou_buf.append(tmp << (8 - ll))
            ou_buf.append(ll)
            #  print(ll, tmp << (8 - ll))

            #  output length for decode
            ll = len(in_buf)
            lt = 0
            while ll:
                lt += 1
                ou_buf.append(ll & 255)
                ll >>= 8
            ou_buf.append(lt)

        #  head information: length of a block
        ll = len(ou_buf)
        cnt = 0
        while ll:
            ou_buf.insert(0, ll & 255)
            ll >>= 8
            cnt += 1
        ou_buf.insert(0, cnt)

        #  output
        output_file.write(ou_buf)

    print('\rprocessing:[{}] {:.2f}% '.format(('*' * 50), 100), end='')
    print('({}B / {}B)'.format(file_size, file_size), end='')
    print('\ntime: {:.2f}s'.format(time.perf_counter() - start), end='')
    input_file.close()
    output_file.close()


def LB_decode(ifn):
    #  input
    input_file = open(ifn, 'rb')
    output_file = open(ifn[:-3], 'wb')

    #  get file size
    file_size = os.path.getsize(ifn)
    sum_size = 0

    #  get present time
    start = time.perf_counter()

    while 1:
        #  input file
        ls = input_file.read(1)
        if ls == b'':
            break

        #  head information : lr : bytes number of lb. lb : length of a block
        lr = ls[0]
        lb = 0
        for i in range(lr):
            x = input_file.read(1)[0]
            lb = lb << 8 | x
        in_buf = input_file.read(lb)

        #  UI
        nt = sum_size / file_size * 100
        print('\rprocessing:[{}] {:.2f}% '.format(('*' * (floor(nt) // 2)) + ('-' * (50 - floor(nt) // 2)), nt), end='')
        print('({}B / {}B)'.format(sum_size, file_size), end='')
        sum_size += len(in_buf)

        if in_buf == b'':
            break
        ou_buf = bytearray()

        #  get p0
        res = 0
        for i in range(p0_len // 8):
            res += in_buf[i] << (Decimal_Number - 8 - i * 8)
        dp = res

        #  extreme condition
        if dp == 0 or dp >> (Decimal_Number - p0_len) == ((1 << p0_len) - 1):
            res = 0
            off = 0
            for x in in_buf[p0_len // 8:]:
                res |= x << off
                off += 8
            tc = 255
            if dp != 0:
                tc = 0
            for i in range(res):
                ou_buf.append(tc)

        #  common condition
        else:
            #  get length
            #  ln : bytes number of lz.  lz : length of a block
            ln = in_buf[-1]
            lz = 0
            now = 0
            for x in in_buf[-ln - 1:-1]:
                lz |= x << now
                now += 8
            in_buf = in_buf[:-ln - 1]

            #  get t, dt
            pos = p0_len
            max_l = len(in_buf) * 8 - 16
            t = []
            for i in range(max_l - p0_len):
                if (in_buf[pos // 8] >> (7 - (pos & 7))) & 1:
                    t.append(1)
                else:
                    t.append(0)
                pos += 1
            for i in range(in_buf[-1]):
                if (in_buf[-2] >> (7 - (pos & 7))) & 1:
                    t.append(1)
                else:
                    t.append(0)
                pos += 1
            #  print(in_buf[-2], in_buf[-1])
            pos = len(t)
            dt = 0
            now = 0
            for i in range(min(pos, Decimal_Number)):
                if t[now] == 1:
                    dt |= 1 << (Decimal_Number - now - 1)
                now += 1

            #  l, r
            tmp = 0
            ll = 0
            dl = 0
            dr = (1 << Decimal_Number) - 1
            for i in range(lz * 8):
                dm = dl + decimal_mul(dp, dr - dl)
                #  print('dl{:77d} dr{:77d} dm{:77d} dt{:77d}'.format(dl, dr, dm, dt))
                if dm > dt:
                    dr = dm
                    tmp = tmp << 1
                    ll += 1
                    if ll == 8:
                        ou_buf.append(tmp)
                        ll = 0
                        tmp = 0
                else:
                    dl = dm
                    tmp = tmp << 1 | 1
                    ll += 1
                    if ll == 8:
                        ou_buf.append(tmp)
                        ll = 0
                        tmp = 0
                while (dl >> (Decimal_Number - 1)) == (dr >> (Decimal_Number - 1)):
                    if dl == dr:
                        print('error')
                        exit(0)
                    if (dl >> (Decimal_Number - 1)) == 0:
                        dl <<= 1
                        dr <<= 1
                        dt <<= 1
                        if now < pos:
                            dt |= t[now]
                            now += 1
                    else:
                        dl -= 1 << (Decimal_Number - 1)
                        dr -= 1 << (Decimal_Number - 1)
                        dt -= 1 << (Decimal_Number - 1)
                        dl <<= 1
                        dr <<= 1
                        dt <<= 1
                        if now < pos:
                            dt |= t[now]
                            now += 1

            #  dm = dl + decimal_mul(dp, dr - dl)
            #  print(dt)
        #  output
        output_file.write(ou_buf)

    print('\rprocessing:[{}] {:.2f}% '.format(('*' * 50), 100), end='')
    print('({}B / {}B)'.format(file_size, file_size), end='')
    print('\ntime: {:.2f}s'.format(time.perf_counter() - start), end='')
    input_file.close()
    output_file.close()


#  LB_encode('pic_original.bmp')
#  LB_decode('pic_original1.bmp.LB')
