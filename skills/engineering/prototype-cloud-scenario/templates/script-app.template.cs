// @: one .NET 10 file-based app, starting point for every rung. Pick ONE shape below, delete the other.
// @: Shape A (rungs 2-4): LightBDD.XUnit3 Basic scenario, keep the Packages/Usings LightBDD+xunit lines.
// @: Shape B (rung 1, single SDK/endpoint call): delete the LightBDD+xunit lines below and the whole Shape A block; keep only Shape B.

#region Packages
#:sdk Microsoft.NET.Sdk
#:property PublishAot=false
#:package {{sdkPackageId}}@{{sdkPackageVersion}}
// @: Shape A only; delete for Shape B
#:package LightBDD.XUnit3@{{lightBddVersion}}
#:package xunit.v3@{{xunitVersion|exact version matching LightBDD.XUnit3's xunit.v3.extensibility.core dependency in its .nuspec; a newer xunit.v3 breaks LightBDD.XUnit3 at runtime}}
#endregion

#region Usings
using System;
// @: add the cloud SDK's using directives here
// @: Shape A only; delete for Shape B
using System.Threading.Tasks;
using LightBDD.Framework;
using LightBDD.Framework.Scenarios;
using LightBDD.XUnit3;
using Xunit;
using Xunit.v3;
#endregion

// ===== Shape A: Scenario (rungs 2-4) =====

[assembly: TestPipelineStartup(typeof(LightBddScope))]

[FeatureDescription(
@"{{featureDescription|In order to ..., as a ..., I want to ...}}")]
public class {{ScenarioSlug|PascalCase}}_feature : FeatureFixture
{
    [Scenario]
    public async Task {{ScenarioTitle|PascalCase, e.g. Symptom_reproduces}}()
    {
        await Runner.RunScenarioAsync(
            Given_broken_state,
            When_the_mechanism_runs,
            Then_the_symptom_is_present
            // @: append When_remediation_applied, Then_the_symptom_is_gone only with a fix option under test
            );
    }

    #region Implementation
    // @: every value, incl. the scenarioTag key/value, from Target environment variables, never literals

    private async Task Given_broken_state()
    {
        // path:line — mirrors {{mirroredCode}}
        // @: create/mutate the resource into the broken end-state; tag every create per Target environment's scenarioTag
    }

    private async Task When_the_mechanism_runs()
    {
        // path:line — mirrors {{mirroredCode}}
    }

    private async Task Then_the_symptom_is_present()
    {
        var observed = await ReadSymptomState();
        Assert.True({{symptomCondition}}, $"expected symptom, observed: {observed}");
    }

    // @: add only with a fix option under test
    private async Task When_remediation_applied()
    {
        // path:line — mirrors {{mirroredCode}}
    }

    private async Task Then_the_symptom_is_gone()
    {
        var observed = await ReadSymptomState();
        Assert.False({{symptomCondition}}, $"expected symptom gone, observed: {observed}");
    }

    private async Task<{{symptomStateType}}> ReadSymptomState()
    {
        // @: single shared read helper reused by both Then steps
        throw new NotImplementedException();
    }
    #endregion
}

// ===== Shape B: Script (rung 1, single SDK/endpoint call) =====
// @: top-level statements; delete Shape A above when using this shape
// @: every value, incl. the scenarioTag key/value, from Target environment variables, never literals

// path:line — mirrors {{mirroredCode}}
{{sdkCall|single SDK/endpoint call with code's exact operation + parameters, tagged per Target environment's scenarioTag}}

var observed = ReadSymptomState();
if ({{symptomCondition}})
{
    Console.WriteLine("{{signalLine|exact symptom signal text}}");
    return 1;
}

Console.WriteLine("symptom not observed");
return 0;

#region Implementation
{{symptomStateType}} ReadSymptomState()
{
    // @: single shared read reused by both the reproduce and validation runs
    throw new NotImplementedException();
}
#endregion
