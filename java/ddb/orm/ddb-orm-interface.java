/*
 * DynamoDB Object Persistence Interface Example - Java Enhanced Client
 *
 * DESCRIPTION:
 * This example demonstrates how to use the DynamoDB Enhanced Client (Object Persistence Interface) to:
 * - Create a table with partition key (PK) and sort key (SK)
 * - Define a Java class to represent table items using annotations
 * - Add items with 2 additional attributes using object instances
 * - Query and scan using object-oriented methods
 * - Clean up by deleting the table
 *
 * The Enhanced Client provides the most object-oriented way to work with DynamoDB
 * by mapping table items to Java POJOs with automatic serialization/deserialization.
 *
 * KEY FEATURES:
 * - Object-oriented approach using annotated Java classes
 * - Automatic serialization/deserialization
 * - Type safety and compile-time validation
 * - Most intuitive interface for Java developers
 * - Built on top of AWS SDK for Java v2
 *
 * USAGE EXAMPLES:
 * 1. Compile and run:
 *    javac -cp ".:aws-java-sdk-dynamodb-enhanced-2.x.x.jar:aws-java-sdk-core-2.x.x.jar" ObjectPersistenceInterface.java
 *    java -cp ".:aws-java-sdk-dynamodb-enhanced-2.x.x.jar:aws-java-sdk-core-2.x.x.jar" ObjectPersistenceInterface
 *
 * 2. With Maven/Gradle, add dependencies and run:
 *    java ObjectPersistenceInterface
 *
 * PREREQUISITES:
 * - AWS credentials configured (AWS CLI, environment variables, or IAM role)
 * - AWS SDK for Java v2 dependencies
 * - DynamoDB permissions (CreateTable, PutItem, Query, DeleteTable)
 *
 * MAVEN DEPENDENCIES:
 * <dependency>
 *   <groupId>software.amazon.awssdk</groupId>
 *   <artifactId>dynamodb-enhanced</artifactId>
 *   <version>2.x.x</version>
 * </dependency>
 */

import software.amazon.awssdk.enhanced.dynamodb.DynamoDbEnhancedClient;
import software.amazon.awssdk.enhanced.dynamodb.DynamoDbTable;
import software.amazon.awssdk.enhanced.dynamodb.Key;
import software.amazon.awssdk.enhanced.dynamodb.TableSchema;
import software.amazon.awssdk.enhanced.dynamodb.mapper.annotations.DynamoDbBean;
import software.amazon.awssdk.enhanced.dynamodb.mapper.annotations.DynamoDbPartitionKey;
import software.amazon.awssdk.enhanced.dynamodb.mapper.annotations.DynamoDbSortKey;
import software.amazon.awssdk.enhanced.dynamodb.model.CreateTableEnhancedRequest;
import software.amazon.awssdk.enhanced.dynamodb.model.QueryConditional;
import software.amazon.awssdk.regions.Region;
import software.amazon.awssdk.services.dynamodb.DynamoDbClient;
import software.amazon.awssdk.services.dynamodb.model.BillingMode;
import software.amazon.awssdk.services.dynamodb.waiters.DynamoDbWaiter;

import java.util.ArrayList;
import java.util.List;

/**
 * DynamoDB Enhanced Client (Object Persistence Interface) Example
 * Demonstrates object-oriented DynamoDB operations using annotated Java classes
 */
public class ObjectPersistenceInterface {

    /**
     * StudentCourse POJO class with DynamoDB Enhanced Client annotations
     * This class represents a student enrolled in a course with their grade
     */
    @DynamoDbBean
    public static class StudentCourse {
        private String studentId;
        private String courseId;
        private String studentName;
        private Integer grade;

        // Default constructor required by DynamoDB Enhanced Client
        public StudentCourse() {}

        public StudentCourse(String studentId, String courseId, String studentName, Integer grade) {
            this.studentId = studentId;
            this.courseId = courseId;
            this.studentName = studentName;
            this.grade = grade;
        }

        @DynamoDbPartitionKey
        public String getStudentId() {
            return studentId;
        }

        public void setStudentId(String studentId) {
            this.studentId = studentId;
        }

        @DynamoDbSortKey
        public String getCourseId() {
            return courseId;
        }

        public void setCourseId(String courseId) {
            this.courseId = courseId;
        }

        public String getStudentName() {
            return studentName;
        }

        public void setStudentName(String studentName) {
            this.studentName = studentName;
        }

        public Integer getGrade() {
            return grade;
        }

        public void setGrade(Integer grade) {
            this.grade = grade;
        }

        @Override
        public String toString() {
            return String.format("StudentCourse{studentId='%s', courseId='%s', studentName='%s', grade=%d}",
                    studentId, courseId, studentName, grade);
        }
    }

    private static final String TABLE_NAME = "Students-ObjectPersistence-Java";
    private static final Region REGION = Region.EU_WEST_2;

    public static void main(String[] args) {
        System.out.println("DynamoDB Enhanced Client (Object Persistence) Demo");
        System.out.println("=".repeat(50));

        // Initialize DynamoDB Enhanced Client
        DynamoDbClient dynamoDbClient = DynamoDbClient.builder()
                .region(REGION)
                .build();

        DynamoDbEnhancedClient enhancedClient = DynamoDbEnhancedClient.builder()
                .dynamoDbClient(dynamoDbClient)
                .build();

        // Create table schema from the annotated class
        DynamoDbTable<StudentCourse> table = enhancedClient.table(TABLE_NAME, 
                TableSchema.fromBean(StudentCourse.class));

        try {
            // 1. Create table
            System.out.println("1. Creating table with Enhanced Client...");
            createTable(table, dynamoDbClient);
            System.out.println("Table '" + TABLE_NAME + "' created successfully");

            // 2. Create and save objects
            System.out.println("\n2. Creating and saving student course objects...");
            List<StudentCourse> students = createSampleStudents();
            
            for (StudentCourse student : students) {
                table.putItem(student);
                System.out.println("✓ Saved: " + student);
            }

            // 3. Query objects by partition key
            System.out.println("\n3. Querying courses for StudentId 'STU001'...");
            List<StudentCourse> aliceCourses = queryByStudent(table, "STU001");
            System.out.println("Found " + aliceCourses.size() + " courses for Alice:");
            for (StudentCourse course : aliceCourses) {
                System.out.println("  - " + course);
            }

            // 4. Get specific object by primary key
            System.out.println("\n4. Getting specific student-course object...");
            StudentCourse specificCourse = getSpecificCourse(table, "STU002", "CS101");
            if (specificCourse != null) {
                System.out.println("  - Found: " + specificCourse);
            } else {
                System.out.println("  - Object not found");
            }

            // 5. Scan all objects
            System.out.println("\n5. Scanning all student-course objects...");
            List<StudentCourse> allCourses = scanAllCourses(table);
            System.out.println("Total objects: " + allCourses.size());
            for (StudentCourse course : allCourses) {
                System.out.println("  - " + course);
            }

            // 6. Demonstrate object modification
            System.out.println("\n6. Modifying and updating an object...");
            if (specificCourse != null) {
                System.out.println("Original grade: " + specificCourse.getGrade());
                specificCourse.setGrade(82); 
                table.putItem(specificCourse);
                System.out.println("Updated grade to: " + specificCourse.getGrade());

                // Verify the update
                StudentCourse updatedCourse = getSpecificCourse(table, "STU002", "CS101");
                if (updatedCourse != null) {
                    System.out.println("Verified updated grade: " + updatedCourse.getGrade());
                }
            }

        } catch (Exception e) {
            System.err.println("Error: " + e.getMessage());
            e.printStackTrace();
        } finally {
            // 7. Clean up - delete table
            System.out.println("\n7. Cleaning up - deleting table...");
            try {
                table.deleteTable();
                
                // Wait for table to be deleted
                DynamoDbWaiter waiter = dynamoDbClient.waiter();
                waiter.waitUntilTableNotExists(builder -> builder.tableName(TABLE_NAME));
                
                System.out.println("Table successfully deleted");
            } catch (Exception e) {
                System.err.println("Failed to delete table: " + e.getMessage());
            }

            // Close clients
            dynamoDbClient.close();
        }
    }

    private static void createTable(DynamoDbTable<StudentCourse> table, DynamoDbClient dynamoDbClient) {
        CreateTableEnhancedRequest createTableRequest = CreateTableEnhancedRequest.builder()
                .billingMode(BillingMode.PAY_PER_REQUEST)
                .build();

        table.createTable(createTableRequest);

        // Wait for table to be active
        DynamoDbWaiter waiter = dynamoDbClient.waiter();
        waiter.waitUntilTableExists(builder -> builder.tableName(TABLE_NAME));
    }

    private static List<StudentCourse> createSampleStudents() {
        List<StudentCourse> students = new ArrayList<>();
        students.add(new StudentCourse("STU001", "CS101", "Alice Johnson", 85));
        students.add(new StudentCourse("STU001", "MATH201", "Alice Johnson", 92));
        students.add(new StudentCourse("STU002", "CS101", "Bob Smith", 78));
        return students;
    }

    private static List<StudentCourse> queryByStudent(DynamoDbTable<StudentCourse> table, String studentId) {
        QueryConditional queryConditional = QueryConditional.keyEqualTo(
                Key.builder().partitionValue(studentId).build()
        );

        List<StudentCourse> results = new ArrayList<>();
        table.query(queryConditional).items().forEach(results::add);
        return results;
    }

    private static StudentCourse getSpecificCourse(DynamoDbTable<StudentCourse> table, 
                                                  String studentId, String courseId) {
        Key key = Key.builder()
                .partitionValue(studentId)
                .sortValue(courseId)
                .build();

        return table.getItem(key);
    }

    private static List<StudentCourse> scanAllCourses(DynamoDbTable<StudentCourse> table) {
        List<StudentCourse> results = new ArrayList<>();
        table.scan().items().forEach(results::add);
        return results;
    }
}
