# LOG

<!-- Append-only problem log, written by droid-log at the end of each session. Entries follow the format fixed in plugins/droid/skills/droid-log/SKILL.md — nothing to fill in here manually. -->

## support-44-dynamodb-harness — 2026-07-31
- **category**: other
- **severity**: note
- **problem**: discovery-gap: missing GOTCHAS.md
- **context**: /home/dev/sources/zic-board/.droid/GOTCHAS.md
- **workaround**: proceeded without it per INPUT Step 3 (pre-phase discovery-gap entry)

## support-44-dynamodb-harness — 2026-07-31
- **category**: convention-conflict
- **severity**: note
- **problem**: VERIFY.md's "Support solution verify" step 2 justifies running `dotnet test support/src/Support.sln --no-build` with no Category filter by claiming "Support.sln's test project has no Category traits — its true integration tests are marked [Fact(Skip=...)]". That is now false: the new `Zerto.InCloud.Support.WebService.IntegrationTests` project carries real, unskipped `Category=IntegrationTest`/`DynamoDB`-tagged tests that need Docker. The step still works today (Docker is available here) but the documented rationale is stale and the step no longer double as a Docker-independent smoke check.
- **context**: .droid/VERIFY.md ("Support solution verify" section, step 2); support/src/Zerto.InCloud.Support.WebService.IntegrationTests/DbDataExporter/DBDataExporterTests.cs
- **workaround**: left VERIFY.md unedited (harness repo, out of scope per task instructions); ran the step as documented since Docker was available, and separately ran the narrowed `Category=IntegrationTest&FullyQualifiedName~DBDataExporterTests` filter per the issue's own Verify section.

## support-44-dynamodb-harness — 2026-07-31
- **category**: other
- **severity**: blocking
- **problem**: Pre-existing production bug surfaced by the new containerized tests: `LogCollectionDbDataResolver.GetTableItemsAsDynamic` built its DynamoDB `Table` via `new TableBuilder(dbClient, tableName).Build()`, which (unlike the pre-migration API) never auto-discovers a table's key schema and unconditionally throws `ArgumentOutOfRangeException` ("A hash key definition is required, call AddHashKey before Build.") unless `AddHashKey` is called first. This was invisible before because the only tests exercising this path were `[Fact(Skip = "for manual execution only")]` and were never actually run. Root cause looks like an unnoticed regression from the "ZIC-5493. Migration AWS SDK to latest" commit (313508acb), which moved AWSSDK.DynamoDBv2 from 3.7.200.23 to 4.0.17.9.
- **context**: support/src/Zerto.InCloud.Support.Platform.Aws.Database/LogCollection/LogCollectionDbDataResolver.cs
- **workaround**: fixed by discovering the table's real key schema via `DescribeTableAsync` and registering it with `TableBuilder.AddHashKey`/`AddRangeKey` before `Build()`, restoring the pre-migration auto-discovery behavior without changing external behavior. This was necessary for the task's acceptance criteria (real, unskipped exporter tests against a container) to be satisfiable at all — flagging here since the task said production log-collection behavior should not change, but the code was already broken and unusable prior to this fix.

## support-44-dynamodb-harness — 2026-07-31
- **category**: other
- **severity**: note
- **problem**: `Zerto.InCloud.Installer.Flows.Jobs.Tests.PostUninstallJobTests.ExecuteZicUninstall_Success_AllMocksCalled` fails consistently (Moq: expected `ISnapshotsCleaner.DeleteSnapshots` exactly 6 times, got 1) both on this branch and on a clean HEAD checkout with none of this task's changes applied (verified via `git stash`) — confirmed pre-existing and unrelated to the Support DynamoDB harness work.
- **context**: installers/src/Tests/Zerto.InCloud.Installer.Flows.Jobs.Tests/PostUninstallJobTests.cs
- **workaround**: none applied (out of scope for this task); left as-is for the owning area to investigate.

## support-46-zero-discovery-folder-skip — 2026-07-31
- **category**: other
- **severity**: note
- **problem**: A genuinely-empty database discovery cannot yet be exercised against the real containerized DynamoDB engine (Verify section's Seam 4 "unseeded" case). `DbNamesAccessor.GetZicCollectionNamesForCurrentLocation()` unconditionally resolves the deployment id via `DeploymentIdAccessor.GetDeploymentId()` (a live `Scan` on the `DeploymentIdentifier` table) before `DBDataExporter`'s zero-tables guard is ever reached; if that table doesn't exist it throws `ResourceNotFoundException`, and if it exists but is empty it throws `InvalidOperationException("Could not resolve deployment Id")`. Additionally, `GetZicCollectionNamesInLocations` unconditionally hardcodes a `DeploymentIdTableName` entry into its result for the current location regardless of DB state, so `allTablesCount` can never genuinely reach `0` via the real accessor as long as the call itself doesn't throw. This is a discovery-layer resilience gap, not a `DBDataExporter` gap — it matches the parent issue's own framing ("once discovery becomes resilient...") and this task's context notes that #47 (which depends on #46) owns discovery resilience, so it was left unaddressed here.
- **context**: support/src/Zerto.InCloud.Support.Platform.Aws.Database/Accessors/DbNamesAccessor.cs; support/src/Zerto.InCloud.Support.Platform.Aws.Database/Accessors/DeploymentIdAccessor.cs; support/src/Zerto.InCloud.Support.WebService.IntegrationTests/DbDataExporter/DBDataExporterTests.cs
- **workaround**: `DBDataExporter`'s zero-tables guard and folder-creation-as-skip logic were unit-tested at the `IDbNamesAccessor`/`IIOUtils` stub seams instead (fully covering the acceptance criteria), and verified end-to-end against the real container for the non-empty-discovery paths. The real-engine "unseeded" case was not added as an integration test; flagging here for whoever picks up #47, since making discovery itself tolerate a missing/empty `DeploymentIdentifier` table is a prerequisite for that scenario to be testable against the real engine.

## support-46-zero-discovery-folder-skip — 2026-07-31
- **category**: other
- **severity**: note
- **problem**: Running the whole-solution unit test loop (`dotnet test all.sln --no-build --filter "Category!=IntegrationTest"`) surfaces 179 failures in `Zerto.InCloud.ApiGateway.IntegrationTests.dll`, all `System.ArgumentNullException: Value cannot be null. (Parameter 'imageIdentifier')` from `AwsEnvironmentResoursesAccessorFactory.Create` during `EnvironmentFixture` construction — the project needs a real AWS environment (image identifiers, network info) that isn't configured in this sandbox, and its tests aren't tagged with a `Category` trait the filter can exclude. Confirmed unrelated to this task's changes (no file in that project or its dependencies was touched).
- **context**: main/src/ApiGateway/Tests/Zerto.InCloud.ApiGateway.IntegrationTests/; main/src/ApiGateway/Tests/Zerto.InCloud.ApiGateway.TestingFramework.Environment.Aws/AwsEnvironmentResoursesAccessorFactory.cs
- **workaround**: none applied (out of scope for this task, pre-existing environment dependency); the Support-only "always-on loop" (`support/src/Support.sln` build + test) passed cleanly, which is this changeset's actual required verify loop per VERIFY.md.

## support-47-per-record-isolation — 2026-07-31
- **category**: convention-conflict
- **severity**: note
- **problem**: Mocking an `internal` interface (`IDynamoDbClientFactory`) declared in `Zerto.InCloud.Support.Platform.Aws.Database` failed at runtime with a Moq/Castle DynamicProxy error ("... is not accessible to the proxy generator used by Moq ...") even though the test assembly (`Zerto.InCloud.Support.IntegrationTests`) already had compile-time `InternalsVisibleTo` access. Castle DynamicProxy additionally needs the *declaring* assembly to grant `InternalsVisibleTo("DynamicProxyGenAssembly2")` at runtime to generate a proxy for an internal type/method — `Zerto.InCloud.Support.Platform.Aws.Database.csproj` granted `InternalsVisibleTo` to three test assemblies but not to `DynamicProxyGenAssembly2`, unlike the sibling `Zerto.InCloud.Support.csproj` which already had it. Good GOTCHAS.md candidate: whenever a new internal interface in an assembly needs to be `Mock<T>`'d by a test, both grants are required, not just the test-assembly one.
- **context**: support/src/Zerto.InCloud.Support.Platform.Aws.Database/Zerto.InCloud.Support.Platform.Aws.Database.csproj; support/src/Zerto.InCloud.Support.Tests/DbNamesAccessorTests.cs
- **workaround**: added `<AssemblyAttribute Include="System.Runtime.CompilerServices.InternalsVisibleTo"><_Parameter1>DynamicProxyGenAssembly2</_Parameter1></AssemblyAttribute>` to the csproj's existing `InternalsVisibleTo` `ItemGroup`; all 11 new `DbNamesAccessorTests` then passed.

## support-47-per-record-isolation — 2026-07-31
- **category**: other
- **severity**: note
- **problem**: Resolved the scope ambiguity flagged by the prior `support-46-zero-discovery-folder-skip` log entries: whether `DeploymentIdAccessor`/`DbNamesAccessor.GetZicCollectionNamesForCurrentLocation()`/`GetZicCollectionNamesInLocations()` unconditionally resolving/hardcoding the deployment-id table falls under this issue's scope. Determination: **out of scope for #47** — the issue's "Affected layers & modules" section explicitly names only `DbNamesAccessor.GetAllLocations()` and `GetAllMemberAccounts()` as the changed methods, and `GetZicCollectionNamesForCurrentLocation`/`GetZicCollectionNamesInLocations`/`DeploymentIdAccessor` are separate methods/class not listed. This task's own acceptance criterion ("every persisted record is bad and discovery yields nothing... does not fail") is satisfied for the two in-scope methods (`GetAllLocations`/`GetAllMemberAccounts` now return empty lists + skips instead of throwing when every record is bad) and is verified at the `IDbNamesAccessor` seam and the containerized harness; the separate pre-existing gap around the `DeploymentIdentifier` table being missing/empty remains unaddressed, as it was in #46.
- **context**: support/src/Zerto.InCloud.Support.Platform.Aws.Database/Accessors/DbNamesAccessor.cs; support/src/Zerto.InCloud.Support.Platform.Aws.Database/Accessors/DeploymentIdAccessor.cs
- **workaround**: none needed — left `DeploymentIdAccessor`/`GetZicCollectionNamesForCurrentLocation`/`GetZicCollectionNamesInLocations`'s `DeploymentIdTableName` hardcoding untouched; flagging here so a milestone reviewer can confirm this determination or file it as a separate follow-up issue if the real-engine "unseeded" integration scenario from #46 is still desired.
