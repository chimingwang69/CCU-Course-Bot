package main

import (
	"fmt"
	"io"
	"net/http"
	"net/url"
	"regexp"
	"strings"
)

/* config */
const (
	id        = ""
	passwd    = ""
	courseID  = ""
	courseNO  = ""
	dept      = ""
	grade     = ""
	cate      = ""
	subcate   = ""
	page      = ""
	credit    = ""
	useragent = "Mozilla/5.0 (X11; Linux; en-US; rv:127.0) Gecko/20160210 Firefox/127.0"
	loginURL  = "http://kiki.ccu.edu.tw/~ccmisp06/cgi-bin/class_new/bookmark.php"
	checkURL  = "http://kiki.ccu.edu.tw/~ccmisp06/cgi-bin/class_new/Add_Course01.cgi"
)

func progress(current, total int) string {
	width := 50 // 進度條寬度
	progress := int(float64(current) / float64(total) * float64(width))
	return fmt.Sprintf("%s%s", strings.Repeat("=", progress), strings.Repeat(" ", width-progress))
}

func sendHTTPRequest(method string, url string, data url.Values) (string, error) {
	client := &http.Client{}
	var req *http.Request
	var err error
	// 創建新的 HTTP POST 請求
	switch method {
	case "POST":
		{
			req, err = http.NewRequest("POST", url, strings.NewReader(data.Encode()))
			if err != nil {
				return "", fmt.Errorf("\n創建請求錯誤: %w", err)
			}
		}
	case "GET":
		{
			req, err = http.NewRequest("GET", url, nil)
			if err != nil {
				return "", fmt.Errorf("\n創建請求錯誤: %w", err)
			}
		}
	default:
		{
			return "", fmt.Errorf("\n無效請求方式")
		}
	}

	// 請求頭
	req.Header.Set("User-Agent", useragent)
	req.Header.Set("Content-Type", "application/x-www-form-urlencoded")

	// 發送
	resp, err := client.Do(req)
	if err != nil {
		return "", fmt.Errorf("\n發送請求錯誤: %w", err)
	}
	defer resp.Body.Close()

	source, err := io.ReadAll(resp.Body)
	if err != nil {
		return "", fmt.Errorf("\n讀取響應錯誤: %w", err)
	}

	// 檢查HTTP Status Code
	if resp.StatusCode != http.StatusOK {
		return "", fmt.Errorf("\n請求失敗 HTTP Status Code: %d", resp.StatusCode)
	}

	return string(source), nil
}

func login(id, passwd string) (string, error) {
	userdata := url.Values{
		"id":       {id},
		"password": {passwd},
	}
	source, err := sendHTTPRequest("POST", loginURL, userdata)
	if err != nil {
		return "", err
	}

	re := regexp.MustCompile(`session_id=([A-Za-z0-9]{36})`)
	match := re.FindStringSubmatch(string(source))
	if len(match) > 1 {
		sessionID := match[1]
		fmt.Printf("登入成功 本次session_id: %s\n", sessionID)
		return sessionID, nil
	}
	re = regexp.MustCompile(`<TITLE>(.+?)</TITLE>`)
	match = re.FindStringSubmatch(string(source))
	return "", fmt.Errorf(match[1])
}

func main() {
	for {
		sessionID, err := login(id, passwd)
		if err != nil {
			fmt.Println("\n登入錯誤:", err)
			goto endprogram
		}

		add_course_data := url.Values{
			"session_id":              {sessionID},
			"dept":                    {dept},
			"grade":                   {grade},
			"cge_cate":                {cate},
			"cge_subcate":             {subcate},
			"SelectTag":               {"1"},
			"page":                    {page},
			"course":                  {courseID + "_" + courseNO},
			courseID + "_" + courseNO: {credit},
		}

		for i := 0; i < 180; i++ {
			fmt.Printf("\r[%-50s] 加選中:%d/180 ", progress(i, 180), i)
			source, err := sendHTTPRequest("POST", checkURL, add_course_data)
			if err != nil {
				fmt.Println("\n錯誤:", err)
				goto endprogram
			}
			if i == 0 {
				re := regexp.MustCompile(`\(星期[一二三四五六日]的第 [A-Z0-9] 堂\) 與 \(星期[一二三四五六日]的第 [A-Z0-9] 堂\)`)
				match := re.FindString(string(source))
				if match != "" {
					fmt.Println("\n衝堂:", match)
					goto endprogram
				}
			}
		}

		final_check_url := "https://kiki.ccu.edu.tw/~ccmisp06/cgi-bin/class_new/Selected_View00.cgi?session_id=" + sessionID
		source, err := sendHTTPRequest("GET", final_check_url, nil)
		if err != nil {
			fmt.Println("\n錯誤:", err)
			goto endprogram
		}
		if strings.Contains(string(source), courseID) {
			fmt.Println("\n加選成功!")
			goto endprogram
		}
	}
endprogram:
}
