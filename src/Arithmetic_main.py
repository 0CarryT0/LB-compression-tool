from Arithmetic_code import LB_decode, LB_encode
import os

if __name__ == '__main__':
    print("----------------------------WELCOM TO LB COMPRESSION TOOL----------------------------")
    print("------If you find any bug or have suggestions, welcome to wechat me: Lb_CarryT-------")
    print("-----------------------------------NOW LET'S START-----------------------------------")
    while 1:
        mode = input("| decode or encode(d/e):")
        bug = 0
        ifn = ''
        if mode[0] == 'd':
            try:
                ifn = input("| path of your file to decode:")
                LB_decode(ifn)
            except:
                print("\n| error!!!")
                bug = 1
            if bug == 0:
                print("\ncompleted!")
            break
        elif mode[0] == 'e':
            try:
                ifn = input("| path of your file to encode:")
                LB_encode(ifn)
            except:
                print("\n| error!!!")
                bug = 1
            if bug == 0:
                print("\ncompleted!")
                compression_ratio = os.path.getsize(ifn + '.LB') / os.path.getsize(ifn) * 100
                print('your compression ratio: {:.2f}%'.format(compression_ratio))
            break
        else:
            print("Hey!!! print true mode!!!")

    print("\n------------------------------copy right: @BUAA_CARRYT-------------------------------")
    print("------If you find any bug or have suggestions, welcome to wechat me: Lb_CarryT-------")
    print("--------------------------------THANK YOU VERY MUCH----------------------------------")
