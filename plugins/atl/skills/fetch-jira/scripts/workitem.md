# [Reporting] ReportingEventHandler fails to send TASK REPORT EXTENDED event when there is an error

When job has an error and error message is 500 characters and more then the ReportingEventHandler builds 17 parameters for TASK REPORT EXTENDED event. But the limit is only 16. As a result, Metrics SDK throws an exception the the Dispatcher fails to send and warning log should be written Failed to emit task {TaskId} extended report event.

In such a case the main TASK REPORT event is published.

It is proposed to fix the issue by removing for extension evention 

metricsBuilder.AddErrorContextIfTaskFailed(task);

**Testing note: if there is no an easy way to creare a job error with 500 symbols message, then it is possible to reproduce the issue with E2E tests.**

**Site Name:**  (production site where the actual problem has happened) 

**SiteID:**  (optional)

**Time:** (in the relevant site time zone)

**Group Name:** (N.A. if irrelevant, e.g. in Pair)

**GroupID:** (N.A. if irrelevant)

**TaskID:**  (N.A. if the problem does not involve a Task)

**Reproducible:**( How many times ? different environments?)

**Workaround:**

**User Actions:**

1. Run a job which ends with an error and the error message longer or equal than 500 characters  
2.  
3.

**Actual Results:**  
1. TASK REPORT event is published  
2.TASK REPORT EXTENDED event isn't published  
3. Warning log is written Failed to emit task {TaskId} extended report event.

**Expected Results:**  
1. TASK REPORT event is published  
2.TASK REPORT EXTENDED event is published

**Configuration Details:**  
Default service configuration
