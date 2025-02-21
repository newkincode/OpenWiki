<!DOCTYPE html>
<html lang="ko">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>검색 결과 - OpenWiki</title>
    <style>
        body {
            font-family: Arial, sans-serif;
            max-width: 800px;
            margin: 40px auto;
            padding: 20px;
            line-height: 1.6;
        }
        h1 {
            color: #333;
        }
        input[type="text"] {
            width: 100%;
            padding: 10px;
            margin-bottom: 10px;
            border: 1px solid #ccc;
            border-radius: 5px;
        }
        button {
            padding: 10px 15px;
            border: none;
            background-color: #007bff;
            color: white;
            border-radius: 5px;
            cursor: pointer;
        }
        button:hover {
            background-color: #0056b3;
        }
        .result {
            margin-top: 20px;
        }
        .result ul {
            list-style: none;
            padding: 0;
        }
        .result li {
            margin-bottom: 10px;
        }
        .result a {
            text-decoration: none;
            color: #007bff;
        }
        .result a:hover {
            text-decoration: underline;
        }
    </style>
</head>
<body>
    <h1>검색</h1>
    <form method="get" action="/search">
        <input type="text" name="query" id="search-box" placeholder="검색어를 입력하세요..." value="{{ query }}">
        <button type="submit">검색</button>
    </form>

    <div class="result">
        {% if results %}
            <ul>
                {% for result in results %}
                    <li><a href="/doc/{{ result }}">{{ result }}</a></li>
                {% endfor %}
            </ul>
        {% else %}
            <p>검색 결과가 없습니다.</p>
        {% endif %}
    </div>
</body>
</html>
