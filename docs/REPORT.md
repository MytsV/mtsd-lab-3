# Команди, конфігурація

Для поданих нижче задач я використовую одні й ті ж команди

```bash
# Збірка образу
docker build -t insert-image-name .
# Збірка за експериментів з кешем
docker build --no-cache -t insert-image-name .
# Вивід інформації про контейнери, у тому числі розміри
docker images
# Запуск контейнера з прив'язкою порта 8080 до випадкового порта на хост-системі
docker run -p 8080 insert-image-name
# Вивід інформації про запущені контейнери, так взнаю порт прив'язки на хост-системі
docker container ls
# Запуск контейнера з прив'язкою порта 8080 до порта 8080 на хост-системі
docker run -p 8080:8080 insert-image-name
# Запуск контейнера з входженням у його оболонку, так перевіряємо вміст
docker run -it insert-image-name sh
# Взнаємо ID останнього запущеного контейнера
docker ps -lq
# Для контейнерів без можливості входження в оболонку, взнаємо вміст
docker export $(docker ps -lq) | tar tf -
# Для контейнерів без можливості входження в оболонку, взнаємо вміст і розміра файлів
docker export $(docker ps -lq) | tar zvtf -
```

Для вимірювання часу збірки образу я використовую [BuildKit](https://github.com/moby/buildkit), попередньо збірки присвоївши змінній середовища DOCKER_BUILDKIT значення 1.

Назви пунктів містять посилання на версію коду. Курсивом виділено назви образів.

# Python

Після кожного кроку збираю образ і запускаю контейнер з прив'язкою 8080 до випадкового, проводжу вимірювання.

## [Завдання 1 - Перший образ](https://github.com/MytsV/mtsd-lab-3/tree/ae67d1b413ddfcfac0dc3211ca90da6744ffed68/python)

*mytsv/python-methologies:v1*

Для того, аби в контейнер не підтягувалися нові версії залежностей, я використала утиліту pipreqs:
```bash
# З кореня репозиторію
cd ./python
pip install pipreqs
pipreqs .
mv ./requirements.txt ./requirements/lock.txt
```
Залежність uvicorn довелось додати вручну [у цей список](https://github.com/MytsV/mtsd-lab-3/blob/ae67d1b413ddfcfac0dc3211ca90da6744ffed68/python/requirements/lock.txt), вказавши останню версію, оскільки pipreqs не включив її автоматично.

```
uvicorn[standard]==0.21.1
```

Опис контейнера застосунку в [Dockerfile](https://github.com/MytsV/mtsd-lab-3/blob/ae67d1b413ddfcfac0dc3211ca90da6744ffed68/python/Dockerfile):
```dockerfile
# Поки що використовуємо важкий базовий образ на основі Debian
FROM python:3.10-bullseye

# Переключаємося на роботу з цією директорією в контейнері
WORKDIR /usr/src/spaceship-app

# Встановлюємо фіксовані залежності
COPY ./requirements/lock.txt ./requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Копіюємо код 
COPY . .

# Запускаємо веб-застосунок разом із контейнером
CMD [ "uvicorn", "spaceship.main:app", "--host=0.0.0.0", "--port=8080" ]
```

<details>
  <summary>Результат:</summary>

<img src="/mtsd-lab-3//app-python.png" alt="result">
</details>

## Завдання 2 - Зміна коду

*mytsv/python-methologies:v2*

Я відредагувала build/index.html (цей файл ігнорується системою контролю версій) наступним чином:
```html
<p>Laboratory assignment 03, <i>finished by Victoria Myts</i></p>
```

<details>
  <summary>Результат:</summary>

<img src="/mtsd-lab-3/pics/app-python-v2.png" alt="result">
</details>

## [Завдання 3 - Менш ефективний Dockerfile](https://github.com/MytsV/mtsd-lab-3/tree/779c65fc8360d39de8dc14e72b8662e5a2416f95/python)

*mytsv/python-methologies:v2-imperfect*

Оскільки спершу порядок команд був ідеальним, у [новому Dockerfile](https://github.com/MytsV/mtsd-lab-3/blob/779c65fc8360d39de8dc14e72b8662e5a2416f95/python/Dockerfile) я змінила їх місцями:

```dockerfile
COPY . .

RUN pip install --no-cache-dir -r ./requirements/lock.txt
```

## [Завдання 4 - Легший базовий образ](https://github.com/MytsV/mtsd-lab-3/tree/eb5fed4c0c917f0dedc423c19c1d90880ffdd368/python)

*mytsv/python-methologies:v2-light*

Змінено перший рядок [Dockerfile](https://github.com/MytsV/mtsd-lab-3/blob/eb5fed4c0c917f0dedc423c19c1d90880ffdd368/python/Dockerfile):
```dockerfile
FROM python:3.10-slim
```

Спершу я випробувала тег 3.10-alpine3.16, але з ним виникали проблеми в наступному пункті при встановленні залежності numpy. Не вистачало певних системних залежностей, як от g++. Аби не стикнутися з подальшими проблемами навіть при встановленні відсутніх системних залежностей, я переробила цей пункт, використовуючи трішки об'ємніший, але працюючий базовий образ.

## [Завдання 5 - Нові залежності](https://github.com/MytsV/mtsd-lab-3/tree/1a1733f41b2580efc5c783ab2177cab74da69a01/python)

**mytsv/python-methologies:v3**

У [spaceship/routers/api.py](https://github.com/MytsV/mtsd-lab-3/blob/1a1733f41b2580efc5c783ab2177cab74da69a01/python/spaceship/routers/api.py) доданий новий ендпоінт /product:
```python
@router.get('/product')
def matrix_product() -> dict:
    import numpy as np

    # Create two 10x10 random matrices
    matrix_a = np.random.rand(10, 10)
    matrix_b = np.random.rand(10, 10)

    # Multiply the matrices together
    result = np.dot(matrix_a, matrix_b)

    return {
        'matrix_a': matrix_a.tolist(), 
        'matrix_b': matrix_b.tolist(), 
        'product': result.tolist()
    }
```

Через pipreqs було оновлено файл зі [списком фіксованих залежностей](https://github.com/MytsV/mtsd-lab-3/blob/1a1733f41b2580efc5c783ab2177cab74da69a01/python/requirements/lock.txt), але версія numpy на моєму пристрої виявилась без підтримки python 3.10, тому я замінила її вручну на новішу.

```
numpy==1.23.0
```

<details>
  <summary>Результат:</summary>

  <img src="/mtsd-lab-3/pics/app-python-v3.png" alt="result">
</details>

Згодом був [створений ще один образ](https://github.com/MytsV/mtsd-lab-3/commit/7d1c90130db3437e6ceaa9216e8da9ff07c052bb) *mytsv/python-methologies:v3-heavy* на основі базового з тегом 3.10-bullseye.

## Виміри й порівняння

<details>
  <summary>Знімки екрану з результатом запуску команд виміру</summary>

  <br>

  <h4>Час збірки</h4>

  Пункт 1
  <img src="/mtsd-lab-3/pics/1-time-python.png" alt="time1">

  Пункт 2
  <img src="/mtsd-lab-3/pics/2-time-python.png" alt="time2">

  Пункт 3
  <img src="/mtsd-lab-3/pics/3-time-python.png" alt="time3">

  Пункт 4
  <img src="/mtsd-lab-3/pics/4-time-python.png" alt="time4">

  Пункт 5 - slim
  <img src="/mtsd-lab-3/pics/5-time-python.png" alt="time5">

  Пункт 5 - bullseye
  <img src="/mtsd-lab-3/pics/5-heavy-time-python.png" alt="time5h">

  <h4>Розмір образу</h4>

  Червоним виділено образ, який створювався з базового python:3.10-alpine3.16

  <img src="/mtsd-lab-3/pics/size-python.png" alt="size">
  <img src="/mtsd-lab-3/pics/size-heavy-python.png" alt="size">

</details>

### Час збірки

З декількох запусків команди ```docker build``` мені стало зрозуміло, що час збірки залежить від багатьох змінних, і не кожна пов'язана з маніпуляціями, проведеними з програмним кодом чи Dockerfile. Оскільки залежності завантажуються, то за кращого у період часу інтернет-з'єдання важкий базовий образ може завантажитися швидше, ніж легший. **Тому тут і надалі я не згадуватиму точний час.**<br>
При більш-менш однакових параметрах мережі, очевидно, швидше проходила збірка образів з меншими базовими образами (**1 пункт** довше за **4 пункт**) або з легшими залежностями (**5 пункт** довше за **4 пункт**).<br>
Завдяки уже завантаженим базовим образам і кешуванню шарів, на 2+ запуску збірки (без змін файлів проєкту) швидкість значно збільшувалась. (**1 пункт** довше за **2 пункт**).<br>
Між **2 і 3 пунктом** я побачила різницю лише у тому, що за зміни порядку команд (і разом з цим шарів) кешування спершу не спрацювало. Після цього я експерементувала зі збіркою, у тому числі застосовуючи прапорець ```--no-cache```. Проте, ніякої "статистичної" відмінності між часом збірки неідеального та оптимізованого порядку шарів я не помітила.

### Розмір образу

Для зручного аналізу створю таблицю:

| Тег/Опис | Розмір |
| ------------- | ------------- |
| v1 | 953MB  |
| v2  | 953MB  |
| v2-imperfect  | 953MB  |
| v2-light  | 166MB  |
| v3  | 233MB  |
| v3-heavy | 1.02GB  |
| База alpine | 94.2MB |

З цього можна зробити висновок, що на розмір образу впливає вибір базового образу (**alpine** < **v2-light** < **v1**) і кількість та важкість залежностей (**v2-light** < **v3**; **v2** < **v3-heavy**).<br>
Для пунктів 2 і 3 у цьому вимірі також майже не виявилось різниці. Я вирішила взнати більш точний розмір обох образів:

<img src="/mtsd-lab-3/pics/precise-size-python.png" alt="size">

Виходить, що "ідеальний" важить навіть на декілька байтів більше! Схоже на те, що причиною цього є додатковий файл із списком залежностей.

## Висновок

<list>
З проведених експериментів я можу виділити такі рекомендації:

- Для того, аби уникнути неочікуваних проблем через підтягування нових версій залежностей у контейнери, можна використовувати різноманітні засоби закріплення залежностей. Для Python проєктів були перевірені утиліти pip freeze і pipreqs.
- Аби зберегти пам'ять пристрою, на якому здійснюється контейнеризація, можна використати більш легку базу образу. Проте, потрібно бути обережним: деякі базові образи при незначному виграші в розмірі викличуть немало важких для виправлення проблем. При пошуку рішень, помилка завантаження деяких залежностей Python на образ з основою Alpine Linux виявилась не унікальною для мене.
- Я не побачила значущої різниці між вимірами ефективності образу з оптимізованим і неоптимізованим порядком шарів. Підозра падає на недостатньо великий розмір моїх Dockerfile'ів. Проте, я вважаю, що ефективним порядком команд усе одно не потрібно нехтувати.
- Оскільки розмір залежностей значно впливає на розмір образу, іноді варто обирати більш lightweight опції, якщо це важливо в зв'язку зі специфіками пристроїв, на яких розгортаємо контейнери. Наприклад, uvicorn[standard] замість uvicorn, або ж tinynumpy замість numpy.
</list>

# Golang

Після кожного кроку збираю образ і запускаю контейнер з прив'язкою 8080 до 8080, проводжу вимірювання.

## [Завдання 1 - Перший образ](https://github.com/MytsV/mtsd-lab-3/tree/21cec80b280e97620c3e3355d7ef034643648d66/golang)

*mytsv/golang-methologies:v1*

Створюю [Dockerfile](https://github.com/MytsV/mtsd-lab-3/blob/21cec80b280e97620c3e3355d7ef034643648d66/golang/Dockerfile) з описом образу:
```dockerfile
# Використовуємо базовий образ на основі alpine
FROM golang:1.17-alpine

WORKDIR /usr/src/fizzbuzz-app

# Встановлюємо залежності
COPY go.mod go.sum ./
RUN go mod download && go mod verify

# Компілюємо бінарний файл
COPY . .
RUN go build -v -o /usr/local/bin/fizzbuzz

#Запускаємо HTTP сервер
CMD ["fizzbuzz", "serve"]
```

<details>
  <summary>Знімки екрану з користувацьким вмістом контейнера</summary>

<img src="/mtsd-lab-3/pics/ls-app.png">
<img src="/mtsd-lab-3/pics/ls-bin.png">
</details>

Крім виконуваного файлу fizzbuzz, як і в проведеній роботі з Python, у файловій системі контейнера знаходиться вихідний код проєкту, опис залежностей, README, Dockerfile і .gitignore. Ці останні складові не потрібні для запуску проєкту.

<details>
  <summary>Результат роботи серверу</summary>

<img src="/mtsd-lab-3/pics/go-app.png">
</details>

## [Завдання 2 - Багатоетапна збірка](https://github.com/MytsV/mtsd-lab-3/tree/7d7a0b683c200ed7e68a8f50498c6a8b3dd06324/golang)

Спершу я підкорегувала перший рядок [Dockerfile](https://github.com/MytsV/mtsd-lab-3/blob/7d7a0b683c200ed7e68a8f50498c6a8b3dd06324/golang/Dockerfile):
```dockerfile 
FROM golang:1.17-alpine AS base
```
давши назву першому етапу збіки, і описала другий етап, залишивши директиву CMD із запуском програми лише у ньому:
```dockerfile
FROM scratch
WORKDIR /root/
COPY --from=base /usr/local/bin/fizzbuzz ./
COPY --from=base /usr/src/fizzbuzz-app/templates ./templates

CMD ["./fizzbuzz", "serve"]
```

<details>
  <summary>Вміст образу</summary>

Наявна мінімальна кількість системних файлів (через специфіку базового образу scratch), перекопійований нами бінарний файл і index.html. Ці користувацьки файли є єдиними необхідними для запуску проєкту.

<img src="/mtsd-lab-3/pics/min-ls.png">
</details>

<details>
  <summary>Проте, цього разу при запуску отримано помилку</summary>

Вона пов'язана з тим, що команда go build без додаткових прапорців/заданих змінних середовища створює <b>динамічний</b> двійковий файл. Він намагається звернутися до спільних бібліотек, але їх немає на образі scratch.

<img src="/mtsd-lab-3/pics/link-error.png">
</details>
Виправляю помилку в Dockerfile, натомість компілюючи **статичний** двійковий файл.

```dockerfile
RUN CGO_ENABLED=0 go build -v -o /usr/local/bin/fizzbuzz
```

<details>
  <summary>Результат:</summary>

<img src="/mtsd-lab-3/pics/go-app-command.png">
</details>

Мінусом користування цим образом є те, що в його оболонку не можна перейти без додаткових налаштувань у Dockerfile. Проте, якщо не турбуватися недоліками статичних бінарних файлів, цей спосіб здався мені досить зручним для наявного завдання.

## [Завдання 3 - Distroless](https://github.com/MytsV/mtsd-lab-3/tree/9a2b65bbdce7bd636991a6185b42ffb0f8c40626/golang)

Для тестування з проєкту distroless я обрала 2 базових образи: static і base. Різниця у тому, що base, на відміну від static, має в собі деякі спільні (shared) бібліотеки.

Відредагувала [Dockerfile](https://github.com/MytsV/mtsd-lab-3/blob/9a2b65bbdce7bd636991a6185b42ffb0f8c40626/golang/Dockerfile), аби другий етап проходив на базі іншого образу:
```dockerfile
FROM gcr.io/distroless/static
```

Також для різноманіття тестування змінила аргументи запуску програми:
```dockerfile
# Генеруємо fizzbuzz completion скрипт для zsh
CMD ["./fizzbuzz", "completion", "zsh"]
```

Збірка і запуск пройшли успішно.

Base образ можна використовувати з динамічним бінарником, для цього змінюємо [Dockerfile](https://github.com/MytsV/mtsd-lab-3/blob/9a2b65bbdce7bd636991a6185b42ffb0f8c40626/golang/Dockerfile):
```dockerfile
RUN go build -o /usr/local/bin/fizzbuzz

FROM gcr.io/distroless/base
```

Тут виникла така ж помилка, як і в пункті 2. Проблема виявилась у використанні alpine версії базового образу golang. Скомпільовані на ньому бінарники містили посилання на такі спільні бібліотеки, яких не було в base. Тому в Dockerfile я замінила базовий образ першого етапу збірки на такий, що має в основі Debian:
```dockerfile
FROM golang AS base
```

<details>
  <summary>Тепер усе працює коректно</summary>

<img src="/mtsd-lab-3/pics/go-fizzbuzz.png">
</details>

Вміст обох образів виявився значно більшим, ніж у того з базою scratch. Проте, користувацькими є також лише виконуваний файл і HTML сторінка.

## Виміри й порівняння

### Час збірки

Як і в роботі з Python, через нестабільність мого інтернет з'єднання я не можу оперувати точними числами. Перша збірка в 3 пункті зайняла менше часу, ніж у 1, оскільки golang базовий образ уже був завантажений, а distroless образи були зовсім невеликими.

### Розмір образу

| Тег/Опис | Розмір |
| ------------- | ------------- |
| v1 | 937MB  |
| v2  | 8.95MB  |
| v3-static  | 12.3MB  |
| v3  | 30.3MB  |

Дуже значною є різниця між першим образом **v1** і тим, **v2**, який створений у багатоетапній збірці. Розмір зменшився більш ніж у 100 разів, при тому, що програма досі запускається належним чином. Звісно, основна причина цьому - це величезна кількість пакетів, встановлених на v1.<br>
Через 3 додаткові пакети в distroless static образі, **v3-static** > **v2**. А динамічні бібліотеки в distroless base додали ще 20МБ понад мінімальним образом scratch.

Недоліком статичних бінарників, а тому й збірки через scratch, повинно було бути те, що вони дуже великі завдяки включеності всіх бібліотек у них. Проте, практика показала протилежне:

| Опис | Розмір |
| ------------- | ------------- |
| Динамічний з v3 | 9892420 |
| Статичний з v2 | 8949506 |

Це майже 1МБ різниці в користь статичного двійкового файлу! Розгляд [цього треда](https://www.reddit.com/r/golang/comments/5lv9jc/why_are_statically_linked_cgo_binaries_smaller/) наводить на думку, що справа у stripping.

## Висновок

Теоретично, код на всіх мовах може бути скомпільований у динамічний чи статичний двійковий файл. Створюючи проєкти, нерідко доцільніше переносити в робочий образ Docker лише цей бінарник і файли, до яких він звертається, а не весь вхідний код. Це сильно зменшить розмір образу за рахунок як вилучення зайвих файлів, так і відсутності пакетів, необхідних для компіляції. Мінімальні базові образи у тому числі можна отримати з проєкту distroless від Google. І хоч є способи статичної компіляції проєктів Python, Java чи JS, тому в теорії навіть для них можна використати scratch, для таких мов непогано використовувати спеціальні мінімальні образи distroless.
Втиснувши у двійковий файл ще й усі бібліотеки, ми зробимо його статичним. У цього є деякі недоліки, які також треба зважувати, але за рахунок такої компіляції розмір образу буде мінімальним.

# [JS](https://github.com/MytsV/mtsd-lab-3/tree/7b99792300b452ad8e8ee62561f6cad2bb64e6ac/js)

За допомогою платформи NodeJS я реалізувала [простий консольний застосунок](https://github.com/MytsV/mtsd-lab-3/blob/7b99792300b452ad8e8ee62561f6cad2bb64e6ac/js/index.js), який виводить ASCII малюнки. Він використовує дві залежності: cat-me і ascii-text-generator.

```js
const catMe = require('cat-me');
const textGenerator = require('ascii-text-generator');

console.log(textGenerator('METH LAB 3', '2'));
console.log(catMe('grumpy'));
```

Мінімально необхідний набір - це буде статичний бінарний файл на базовому образі scratch. Такий можна створити, провівши бандлінг за допомогою **esbuild** та компіляцію за допомогою **pkg**. <br>
У [package.json](https://github.com/MytsV/mtsd-lab-3/blob/7b99792300b452ad8e8ee62561f6cad2bb64e6ac/js/package.json) потрібно було налаштувати опції запуску pkg. За статичну компіляцію відповідає ціль з linuxstatic, а параметр bin задає те, який файл скомпілюється в двійковий файл. build.cjs створюється утилітою esbuild.
```json
"bin": "build.cjs",
"pkg": {
    "targets": [
        "node12-linuxstatic-x64"
    ]
}
```
Всі ці операції описані в [Dockerfile](https://github.com/MytsV/mtsd-lab-3/blob/7b99792300b452ad8e8ee62561f6cad2bb64e6ac/js/Dockerfile) з багатоетапною збіркою:
```dockerfile
FROM node as builder
WORKDIR /app
# Копіюємо лише потрібні файли
COPY package.json package-lock.json index.js ./
# Встановлюємо лише production залежності
RUN npm install --prod
RUN npm install -g esbuild
RUN npm install -g pkg
# Збираємо код в один файл build.cjs
RUN npx esbuild index.js  --bundle --outfile=build.cjs --format=cjs --platform=node
# Компілюємо
RUN pkg .

# В мінімальний образ перекопійовуємо лише бінарник
FROM scratch
WORKDIR /app
COPY --from=builder /app/hello-world /app/
CMD ["./hello-world"]
```
<details>
  <summary>Результат запуску контейнера</summary>

<img src="/mtsd-lab-3/pics/js-app.png">
</details>

<details>
  <summary>Розмір образу</summary>

<img src="/mtsd-lab-3/pics/js-size.png">
</details>

<details>
  <summary>Вміст образу</summary>

<img src="/mtsd-lab-3/pics/js-ls.png">
</details>

## Висновок

Мінімальний образ вийшов крихітним - лише 30 МБ. Проте, саме для JS підхід із двійковими файлами дуже незручний. Інформацію знайти нелегко, а якщо якась залежність використовує файли - робота стає ще на порядок важчою. На мою думку, для контейнеризації проєктів, розроблених на NodeJS, найкраще використовувати мінімальні базові образи, специфічні для NodeJS, як такий від проєкту distroless, а також команду npm-prune. Такий образ у мене займав близько 180 МБ, але його створення зайняло менше часу, та й він буде більш підтримуваним.

# Загальні висновки

Більшість висновків і рекомендацій написано після завдань. Хочу лиш додати те, що побачила як спільне для всіх пунктів: не завжди максимальна оптимізація виправдовує затрачені на неї час і сили. У цілому, контейнери видались мені чудовим засобом для розгортання застосунків.