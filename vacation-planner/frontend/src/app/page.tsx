<<<<<<< HEAD
"use client";

import { useRouter } from "next/navigation";
import { MarketingHero } from "@/components/marketing/MarketingHero";
import { SocialProof } from "@/components/marketing/SocialProof";
import { FeatureGrid } from "@/components/marketing/FeatureGrid";
import { ProductPreview } from "@/components/marketing/ProductPreview";
import { DestinationGrid } from "@/components/marketing/DestinationGrid";
import { HowItWorks } from "@/components/marketing/HowItWorks";
import { CollaborationSection } from "@/components/marketing/CollaborationSection";
=======
import { MarketingHero } from "@/components/marketing/MarketingHero";
import { FeatureGrid } from "@/components/marketing/FeatureGrid";
import { HowItWorks } from "@/components/marketing/HowItWorks";
import { ProductPreview } from "@/components/marketing/ProductPreview";
import { DestinationGrid } from "@/components/marketing/DestinationGrid";
import { CollaborationSection } from "@/components/marketing/CollaborationSection";
import { SocialProof } from "@/components/marketing/SocialProof";
>>>>>>> DEV-17-Change-frontend-color-theme
import { MarketingCTA } from "@/components/marketing/MarketingCTA";
import { MarketingFooter } from "@/components/marketing/MarketingFooter";

export default function Home() {
<<<<<<< HEAD
  const router = useRouter();
  const goToPlanner = () => router.push("/plan");

  return (
    <div className="flex min-h-screen flex-col bg-[#020204] text-white">
      <MarketingHero onStartPlanning={goToPlanner} />
      <SocialProof />
      <FeatureGrid />
      <ProductPreview />
      <DestinationGrid />
      <HowItWorks />
      <CollaborationSection />
      <MarketingCTA onStartPlanning={goToPlanner} />
      <MarketingFooter />
    </div>
=======
  return (
    <main>
      <MarketingHero />
      <FeatureGrid />
      <HowItWorks />
      <ProductPreview />
      <DestinationGrid />
      <CollaborationSection />
      <SocialProof />
      <MarketingCTA />
      <MarketingFooter />
    </main>
>>>>>>> DEV-17-Change-frontend-color-theme
  );
}
