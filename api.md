# API

> 🔌 API document of server

## Plant-identify

Url: **/id**

Method: **POST**

Body: {
    image: file with extension png, jpg, jpeg or bmp
}

Return：List\<String\> names 最可能的5个植物名称

## Plant-distinguish

Url: **/compare**

Method: **POST**

Body: {
    src: file with extension png, jpg, jpeg or bmp, // 想要分辨的源图像
    dst: file with extension png, jpg, jpeg or bmp // 想要与之分辨的目标图像
}

如拍的照片为src，要与dst比较

Return: flag(boolean)

## Plant-exception-detection

Url: **/detect**

Method: **POST**

Body: {
    image: file with extension png, jpg, jpeg or bmp
}

Return: code(string) 异常种类
