import { defineProof } from "../kit";

export const apiAnswers = defineProof("api-answers", ["api-response"], async ctx => {
  const response = await ctx.observe<{ status: number }>("api-response", { path: "/" });
  return { pass: response.status < 500, expected: "an answer below 500", actual: response.status, hint: "The API did not answer well. Is the app up and the build fresh? pnpm mole doctor" };
});
