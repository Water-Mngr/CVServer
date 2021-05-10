# API

> 🔌 API document of server

## Plant-identify

1. Url: **/id**

    Method: **POST**

    Body: {
        image: file with extension png, jpg, jpeg or bmp
    }

    Return: JSON { class_names: string, intro: string(植物介绍), advice: string(浇水建议)}

2. Url: **/id/list**

    Method: **POST**

    Body: {
        image: file with extension png, jpg, jpeg or bmp
    }

    Return：JSON {
        class_names: [ String ] (最可能的5个植物中文名称),
        probs: [ float ] (对应的概率)
    }

## Plant-distinguish

Url: **/compare**

Method: **POST**

Body: {
    src: file with extension png, jpg, jpeg or bmp, // 想要分辨的源图像
    dst: file with extension png, jpg, jpeg or bmp // 想要与之分辨的目标图像
}

如拍的照片为src，要与dst比较

Return: JSON: { similarity: float (相似度，＞ 1可认定为同一植物)}

## Plant-exception-detection

Url: **/detect**

Method: **POST**

Body: {
    image: file with extension png, jpg, jpeg or bmp
}

Return: JSON: { problems: string (异常种类) }
