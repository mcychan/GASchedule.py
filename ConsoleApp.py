import codecs
import pathlib
import os
import sys
import tempfile
import time
import traceback

import Configuration
# import GeneticAlgorithm
# import NsgaII
# import Ngra
import Amga2
import HtmlOutput


def main(file_name):
    try:
        start_time = int(round(time.time() * 1000))

        configuration = Configuration.Configuration()
        target_file = str(pathlib.Path().absolute()) + file_name
        configuration.parseFile(target_file)

        # alg = GeneticAlgorithm.GeneticAlgorithm(configuration)
        alg = Amga2.Amga2(configuration)
        print("GaSchedule Version 1.2.0 . Making a Class Schedule Using", alg, ".\n")
        print("Copyright (C) 2021 Miller Cy Chan.\n")
        alg.run()
        html_result = HtmlOutput.HtmlOutput.getResult(alg.result)

        temp_file_path = tempfile.gettempdir() + file_name.replace(".json", ".htm")
        writer = codecs.open(temp_file_path, "w", "utf-8")
        writer.write(html_result)
        writer.close()

        seconds = (int(round(time.time() * 1000)) - start_time) / 1000.0
        print("\nCompleted in {} secs.\n".format(seconds))
        os.startfile(temp_file_path)
    except:
        traceback.print_exc()


if __name__ == "__main__":
    try:
        file_name = sys.argv[1]
    except IndexError:
        file_name = "/GaSchedule.json"
    main(file_name)
