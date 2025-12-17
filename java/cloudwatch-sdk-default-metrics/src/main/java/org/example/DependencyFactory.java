
package org.example;

import software.amazon.awssdk.http.apache.ApacheHttpClient;
import software.amazon.awssdk.metrics.MetricPublisher;
import software.amazon.awssdk.metrics.publishers.cloudwatch.CloudWatchMetricPublisher;
import software.amazon.awssdk.services.s3.S3Client;

import javax.swing.plaf.synth.Region;
import java.time.Duration;

/**
 * The module containing all dependencies required by the {@link Handler}.
 */
public class DependencyFactory {

    private DependencyFactory() {}

    /**
     * @return an instance of S3Client
     */
    public static S3Client s3Client() {

        MetricPublisher metricsPub = CloudWatchMetricPublisher.builder()
                .uploadFrequency(Duration.ofSeconds(5L))
                .namespace("AwsSdk/JavaSdk2")
                .build();

        /*
        The default httpClient is Apache for Synchronous S3Client (not actually needed to explicitly mention below).
        Registering CloudWatch meteric for S3 SDK Api calls
         */
        return S3Client.builder()
                        .httpClientBuilder(ApacheHttpClient.builder())
                        .overrideConfiguration(c -> c.addMetricPublisher(metricsPub))
                        .build();
    }
}
