"use client";

import { useRouter } from "next/navigation";
import { MarketingHero } from "@/components/marketing/MarketingHero";
import { FeatureGrid } from "@/components/marketing/FeatureGrid";
import { HowItWorks } from "@/components/marketing/HowItWorks";
import { ProductPreview } from "@/components/marketing/ProductPreview";
import { DestinationGrid } from "@/components/marketing/DestinationGrid";
import { CollaborationSection } from "@/components/marketing/CollaborationSection";
import { SocialProof } from "@/components/marketing/SocialProof";
import { MarketingCTA } from "@/components/marketing/MarketingCTA";
import { MarketingFooter } from "@/components/marketing/MarketingFooter";

export default function Home() {
  const router = useRouter();
  const goToPlan = () => router.push("/plan");

  return (
    <main>
      <MarketingHero onStartPlanning={goToPlan} />
      <FeatureGrid />
      <HowItWorks />
      <ProductPreview />
      <DestinationGrid />
      <CollaborationSection />
      <SocialProof />
      <MarketingCTA onStartPlanning={goToPlan} />
      <MarketingFooter />
    </main>
  );
}
