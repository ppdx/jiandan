# jiandan
用来爬取煎蛋上的图啦～～～

是用scrapy写的，就当做是课后实践来的啦

感觉写的比较乱

有一个最大的bug就是老是被煎蛋给封掉IP（其实是我懒的设置速度啦）

现在使用的话呢，其实就是把脚本设置到开机运行的状态，然后其实爬下来也并没有什么用啦

打算后面再去写一个可以用来看图的软件呢（好吧其实估计没有太大的希望啦）

使用挺简单的，直接运行`./start`就可以从最新的一直一直爬到上次爬到的页面啦，
所有的数据都是存到sqlite数据库里面（主要是懒得自己设计文件格式了）

`./start`后面可以跟两个参数可选参数，第一个是从第几页开始运行（要大于8000啦，再往前的煎蛋都删掉啦，哭），
第二个参数是表示一共爬多少页（其实并没有什么用，一般爬个40页就被封IP了。。。）

也可以使用scrapy的命令`scrapy crawl pic [-a start=<start-page-number>] [-a length=<how-much-pages-you-want>]`
