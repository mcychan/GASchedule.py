# GASchedule.py
Making a Class Schedule Using a Genetic Algorithm with Python

Port from C# .NET core
https://github.com/mcychan/GASchedule.cs

<img src="https://i.stack.imgur.com/QDPIS.png" /></p>
# How to call this api
If you are using Python, you would call GASchedule as follows:

```python
    file_name = "/GaSchedule.json"
    start_time = int(round(time.time() * 1000))

    configuration = Configuration.Configuration()
    target_file = str(pathlib.Path().absolute()) + file_name
    configuration.parseFile(target_file)

    alg = NsgaII.NsgaII(configuration)
    alg.run()
    html_result = HtmlOutput.HtmlOutput.getResult(alg.result)
```
