package hk.edu.gaSchedule;

import java.awt.Desktop;
import java.io.BufferedWriter;
import java.io.File;
import java.io.FileOutputStream;
import java.io.OutputStreamWriter;

// import hk.edu.gaSchedule.algorithm.Amga2;
import hk.edu.gaSchedule.algorithm.GaQpso;
import hk.edu.gaSchedule.algorithm.NsgaIII;
import hk.edu.gaSchedule.model.Configuration;
import hk.edu.gaSchedule.model.Schedule;

public class ConsoleApp
{
    public static void main(String[] args)
    {
    	try {	
	        final String FILE_NAME = args.length > 0 ? args[0] : "GaSchedule.json";
	        final long startTime = System.currentTimeMillis();

	        Configuration configuration = new Configuration();
	        File targetFile = new File(System.getProperty("user.dir") + "/" + FILE_NAME);
	        if(!targetFile.exists())
	        	targetFile = new File(new File(ConsoleApp.class.getResource("/").toURI()).getParentFile() + "/" + FILE_NAME);
	        configuration.parse(targetFile);	        
	        
	        GaQpso<Schedule> alg = new GaQpso<>(new Schedule(configuration), 2, 2, 80, 3);
	        // Amga2<Schedule> alg = new Amga2<>(new Schedule(configuration), 0.35f, 2, 80, 3);
	        System.out.println(String.format("GaSchedule Version %s . Making a Class Schedule Using %s.", "1.2.5", alg.toString()));
	        System.out.println("Copyright (C) 2022 - 2024 Miller Cy Chan.");
	        alg.run(9999, 0.999);
	        
	        String htmlResult = HtmlOutput.getResult(alg.getResult());
	
	        String tempFilePath = System.getProperty("java.io.tmpdir") + FILE_NAME.replace(".json", ".htm");
	        try(BufferedWriter writer = new BufferedWriter(new OutputStreamWriter(new FileOutputStream(tempFilePath))))
	        {
	            writer.write(htmlResult);
	            writer.flush();
	        }
	
	        double seconds = (System.currentTimeMillis() - startTime) / 1000.0;
	        System.out.println(String.format("\nCompleted in %f secs.", seconds));
	        if (Desktop.isDesktopSupported()) {
	            try {
	                Desktop.getDesktop().open(new File(tempFilePath));
	            } catch (Exception ex) {
	                // no application registered for html
	            }
	        }
    	}
    	catch(Exception ex) {
    		ex.printStackTrace();
    	}
    }
}
