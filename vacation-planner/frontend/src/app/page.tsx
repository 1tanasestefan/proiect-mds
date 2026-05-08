"use client";

import { useRouter } from "next/navigation";
import { MarketingHero } from "@/components/marketing/MarketingHero";
import { SocialProof } from "@/components/marketing/SocialProof";
import { FeatureGrid } from "@/components/marketing/FeatureGrid";
import { ProductPreview } from "@/components/marketing/ProductPreview";
import { DestinationGrid } from "@/components/marketing/DestinationGrid";
import { HowItWorks } from "@/components/marketing/HowItWorks";
import { CollaborationSection } from "@/components/marketing/CollaborationSection";
import { MarketingCTA } from "@/components/marketing/MarketingCTA";
import { MarketingFooter } from "@/components/marketing/MarketingFooter";

export default function Home() {
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
  );
}
