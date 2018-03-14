// perfrunner
package main

import (
	"flag"
	"fmt"
	"os"
	"time"

	vegeta "github.com/tsenart/vegeta/lib"
)

func main() {
	// Define command-line parameters
	baseURL := flag.String("baseURL", "http://www.example.com", "the start of the url to attack")
	rate := flag.Int("rate", 1, "requests per second")
	timeout := flag.Int("timeout", 5, "time before request is cancelled, minutes")
	duration := flag.Int("duration", 60, "seconds to run test")
	flag.Parse()

	// Print the settings used.
	fmt.Printf("Attacking base URL, %v\n", *baseURL)
	fmt.Printf("At %v times per second\n", *rate)
	fmt.Printf("For %v seconds\n", *duration)

	// Create the results file.
	t := time.Now()
	filename := fmt.Sprintf("load_results/%v_R%v.csv", t.Format("2006-01-02_15.04.05"), *rate)
	f, err := os.Create(filename)
	check(err)

	// Build the URL,
	url := *baseURL
	// then use it to create the Target.
	target := vegeta.Target{
		Method: "GET",
		URL:    url,
	}

	// Run vegeta attack
	timeDuration := time.Duration(*duration) * time.Second
	timeoutDuration := time.Duration(*timeout) * time.Minute
	targeter := vegeta.NewStaticTargeter(target)
	attacker := vegeta.NewAttacker(vegeta.Timeout(timeoutDuration))
	var metrics vegeta.Metrics
	results := attacker.Attack(targeter, uint64(*rate), timeDuration)
	for res := range results {
		metrics.Add(res)
		vegeta.NewCSVEncoder(f).Encode(res)
	}
	metrics.Close()

	// Examine Results, and determine pass/fail
	for code, count := range metrics.StatusCodes {
		fmt.Printf("Total %3v received: %3v\n", code, count)
	}
	fmt.Printf("Total Duration: %v\n", metrics.Duration.Seconds())
	fmt.Printf("Success Rate: %v\n", metrics.Success)
	fmt.Printf("Errors: %v\n", metrics.Errors)
	fmt.Printf("Average Response Time: %v\n", metrics.Latencies.Mean)
	fmt.Printf("Longest Response Time: %v\n", metrics.Latencies.Max)
}

func check(e error) {
	if e != nil {
		panic(e)
	}
}
