from selenium import webdriver
from time import sleep
import requests
from os import makedirs,path

def addCookie(domain,cookies,driver):
    driver.get(domain) #先加载域名，让其知道在哪个网站添加
    driver.delete_all_cookies() #删除原来的cookie
    cookies = cookies.split("; ") #划分cookie为列表
    for cookie in cookies:
        cookie = cookie.split("=", 1) #只分割一次“=”，适应cookie里边有“=”出现的情况
        driver.add_cookie({"name": cookie[0], "value": cookie[1]}) #将cookie变为{"name":"","value":""}的列表。Note：如果出错，请确保cookie无误
    return driver

def getPicById(id,driver):
    titles = list() #图片标题
    links = list() #图片链接
    pic = list() #图片所有属性
    page = 1 #当前页码
    pages = 1 #页数

    driver.get("https://www.pixiv.net/member_illust.php?id=" + id + "&p=" + str(page))
    #判断图片是否全部加载完成
    while len(links)<len(titles) or len(links)==0 or page<=pages:
        # 浏览器滚到最下方
        driver.execute_script("window.scrollTo(0,document.body.scrollHeight)")
        sleep(1)
        # 点击返回顶部按钮，解决懒加载问题
        goToTop = driver.find_element_by_xpath("//button[@class='_3cJzhTE']")
        driver.implicitly_wait(5)
        goToTop.click()
        sleep(1)
        #如果在第一页则所有获取页数
        if page == 1 :
            pages = driver.find_elements_by_xpath("//div[@class='_1zRQ9vu']//a")
            pages = len(pages)-1
        #获取图片标题
        titles = driver.find_elements_by_xpath("//a[@class='sc-fzXfPK hWjVLb']")
        #获取图片对象
        links = driver.find_elements_by_xpath("//img[@class='sc-fzXfPe kfVsju']")
        #获取图片href
        hrefs = driver.find_elements_by_xpath("//a[@class='sc-fzXfOZ bSzUTS']")
        if len(titles)==len(links) and len(titles)!=0:
            for i in range(len(titles)):
                pic.append([
                    titles[i].text.replace("?","").replace("*","").replace("/","")
                        .replace("\\","").replace(">","").replace("<","").replace("|","").replace(":",""),
                    links[i].get_attribute("src").replace("c/250x250_80_a2/img-master", "img-original")
                        .replace("_square1200", ""),
                    hrefs[i].get_attribute("href")
                ])
            print("\r获取第", page, "/", pages, "页完成",end="")
            page = page+1 #页码加1
            driver.get("https://www.pixiv.net/member_illust.php?id=" + id + "&p=" + str(page)) #获取新页面
    return pic

def downPic(pic,id):
    errorInfo = list()
    for i in range(len(pic)):
        try:
            dir = "./pic/"+str(id)
            fileName = dir+"/"+pic[i][0]+".jpg"
            if not path.exists(dir):
                makedirs(dir)
            data = requests.get(pic[i][1],headers={"referer":pic[i][2]})
            if data.status_code==404 :
                data = requests.get(pic[i][1].replace("jpg","png"), headers={"referer": pic[i][2]})
                fileName = dir+"/"+pic[i][0]+".png"
            with open(fileName, 'wb') as f:
                f.write(data.content)
                f.close()
            print("\r已下载",i+1,"/",len(pic),"\t",pic[i][0],end= "")
            sleep(1)
        except Exception as e:
            errorInfo.append(str(i)+"\t"+str(e))
    print("\r已下载",len(pic)-len(errorInfo),",错误",len(errorInfo))
    for error in errorInfo:
        print(error)


if __name__ == '__main__':
    driver = webdriver.Chrome(r"C:\Program Files (x86)\Google\Chrome\Application\chromedriver") #需要设置的地方
    url = "https://www.pixiv.net/"
    cookies = "" #需要设置的地方
    driver = addCookie(url,cookies,driver)
    id = input("输入画师id：") #432150
    pic = getPicById(id,driver)
    downPic(pic,id)
    driver.close()