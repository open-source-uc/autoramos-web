import imageio.v3 as iio

def path_to_image(path):
    return iio.imread(path)


alphabet = {
    "0": path_to_image('captcha/Alphabet/0.bmp'),
    "1": path_to_image('captcha/Alphabet/1.bmp'),
    "2": path_to_image('captcha/Alphabet/2.bmp'),
    "3": path_to_image('captcha/Alphabet/3.bmp'),
    "4": path_to_image('captcha/Alphabet/4.bmp'),
    "5": path_to_image('captcha/Alphabet/5.bmp'),
    "6": path_to_image('captcha/Alphabet/6.bmp'),
    "7": path_to_image('captcha/Alphabet/7.bmp'),

    "8": path_to_image('captcha/Alphabet/8.bmp'),
    "8_alt": path_to_image('captcha/Alphabet/8_alt.bmp'),

    "9": path_to_image('captcha/Alphabet/9.bmp'),
    "9_alt": path_to_image('captcha/Alphabet/9_alt.bmp'),


    "A": path_to_image('captcha/Alphabet/A.bmp'),
    "B": path_to_image('captcha/Alphabet/B.bmp'),
    "C": path_to_image('captcha/Alphabet/C.bmp'),
    "D": path_to_image('captcha/Alphabet/D.bmp'),
    "E": path_to_image('captcha/Alphabet/E.bmp'),
    "F": path_to_image('captcha/Alphabet/F.bmp'),
    "G": path_to_image('captcha/Alphabet/G.bmp'),

    "H": path_to_image('captcha/Alphabet/H.bmp'),
    "H_alt": path_to_image('captcha/Alphabet/H_alt.bmp'),

    "I": path_to_image('captcha/Alphabet/I.bmp'),
    "J": path_to_image('captcha/Alphabet/J.bmp'),
    "K": path_to_image('captcha/Alphabet/K.bmp'),
    "L": path_to_image('captcha/Alphabet/L.bmp'),
    "M": path_to_image('captcha/Alphabet/M.bmp'),
    "N": path_to_image('captcha/Alphabet/N.bmp'),
    "O": path_to_image('captcha/Alphabet/O.bmp'),
    "P": path_to_image('captcha/Alphabet/P.bmp'),
    "R": path_to_image('captcha/Alphabet/R.bmp'),
    "S": path_to_image('captcha/Alphabet/S.bmp'),
    "T": path_to_image('captcha/Alphabet/T.bmp'),
    "U": path_to_image('captcha/Alphabet/U.bmp'),
    "V": path_to_image('captcha/Alphabet/V.bmp'),
    "Z": path_to_image('captcha/Alphabet/Z.bmp')
}