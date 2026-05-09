import { expect, test } from "@playwright/test";

test.describe("VibeTrips smoke flows", () => {
  test.beforeEach(async ({ page }) => {
    await page.route("**/_next/image*", (route) => route.abort());
  });

  test("home page renders without redirecting to the planner", async ({ page }) => {
    await page.goto("/");

    await expect(page).toHaveURL("/");
    await expect(page.getByText("AI-Powered Travel Planning", { exact: true })).toBeVisible();
    await expect(page.getByRole("heading", { name: /Plan unforgettable/i })).toBeVisible();
    await expect(
      page.getByRole("navigation").getByRole("link", { name: "How It Works" })
    ).toBeVisible();
  });

  test("home page start planning CTA opens the planner", async ({ page }) => {
    await page.goto("/");

    await page.getByRole("button", { name: "Start Planning — Free" }).click();

    await expect(page).toHaveURL("/plan");
    await expect(page.getByRole("heading", { name: "CRAFT YOUR JOURNEY" })).toBeVisible();
    await expect(page.getByRole("heading", { name: "How do you want to plan?" })).toBeVisible();
  });

  test("planner page renders the trip planning choices", async ({ page }) => {
    await page.goto("/plan");

    await expect(page.getByRole("heading", { name: "CRAFT YOUR JOURNEY" })).toBeVisible();
    await expect(page.getByRole("button", { name: /I am flexible/i })).toBeVisible();
    await expect(page.getByRole("button", { name: /I know the destination/i })).toBeVisible();
  });

  test("login page is configured and app navigation is present", async ({ page }) => {
    await page.goto("/login");

    await expect(page.getByRole("heading", { name: "Welcome Back" })).toBeVisible();
    await expect(page.getByRole("button", { name: "Sign In" })).toBeEnabled();
    await expect(page.getByRole("link", { name: "Plan a Trip" })).toBeVisible();
    await expect(page.getByRole("link", { name: "Discover" })).toBeVisible();
    await expect(page.getByRole("link", { name: "My Trips" })).toBeVisible();
  });
});
