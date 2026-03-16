import { motion } from "motion/react";
import { useState } from "react";
import Image from "next/image";
import { 
  Wallet, 
  Heart, 
  Zap, 
  Moon, 
  PartyPopper, 
  Eye, 
  UtensilsCrossed,
  MapPin,
  Users,
  ArrowRight
} from "lucide-react";

interface FormData {
  budget: string;
  lifestyle: string;
  vacationType: string;
  destination: string;
  travelers: string;
}

export function InputFormSection({ onSubmit }: { onSubmit: (data: FormData) => void }) {
  const [currentStep, setCurrentStep] = useState(0);
  const [formData, setFormData] = useState<FormData>({
    budget: "",
    lifestyle: "",
    vacationType: "",
    destination: "",
    travelers: "",
  });

  const steps = [
    { id: "budget", title: "Budget Tier" },
    { id: "lifestyle", title: "Your Lifestyle" },
    { id: "vacationType", title: "Vacation Type" },
    { id: "destination", title: "Destination" },
    { id: "travelers", title: "Travelers" },
  ];

  const budgetOptions = [
    { id: "low", label: "Budget Explorer", icon: Wallet, desc: "Smart spending, big adventures", gradient: "from-emerald-500 to-teal-500" },
    { id: "medium", label: "Comfort Seeker", icon: Heart, desc: "Balance of value and comfort", gradient: "from-blue-500 to-cyan-500" },
    { id: "luxury", label: "Luxury Voyager", icon: Zap, desc: "Premium all the way", gradient: "from-purple-500 to-pink-500" },
  ];

  const lifestyleOptions = [
    { id: "relaxed", label: "Relaxed", icon: Heart, desc: "Slow-paced and serene", gradient: "from-rose-400 to-orange-400" },
    { id: "energetic", label: "Energetic", icon: Zap, desc: "Action-packed days", gradient: "from-yellow-400 to-red-500" },
    { id: "nightowl", label: "Night Owl", icon: Moon, desc: "After-dark explorer", gradient: "from-indigo-500 to-purple-600" },
  ];

  const vacationTypeOptions = [
    { id: "party", label: "Partying", icon: PartyPopper, desc: "Nightlife & celebrations", image: "https://images.unsplash.com/photo-1611464379978-2415d1678256?crop=entropy&cs=tinysrgb&fit=max&fm=jpg&ixid=M3w3Nzg4Nzd8MHwxfHNlYXJjaHwxfHxuaWdodGxpZmUlMjBjbHViJTIwcGFydHklMjBuZW9ufGVufDF8fHx8MTc3MzY3Mjg1MXww&ixlib=rb-4.1.0&q=80&w=1080" },
    { id: "sightseeing", label: "Sightseeing", icon: Eye, desc: "Culture & landmarks", image: "https://images.unsplash.com/photo-1600209892743-c50f8091b231?crop=entropy&cs=tinysrgb&fit=max&fm=jpg&ixid=M3w3Nzg4Nzd8MHwxfHNlYXJjaHwxfHxiYWxpJTIwdGVtcGxlJTIwc3Vuc2V0JTIwYXJjaGl0ZWN0dXJlfGVufDF8fHx8MTc3MzY3Mjg1MHww&ixlib=rb-4.1.0&q=80&w=1080" },
    { id: "culinary", label: "Culinary", icon: UtensilsCrossed, desc: "Food-focused journey", image: "https://images.unsplash.com/photo-1643757343278-5d50309dfa44?crop=entropy&cs=tinysrgb&fit=max&fm=jpg&ixid=M3w3Nzg4Nzd8MHwxfHNlYXJjaHwxfHxnb3VybWV0JTIwZm9vZCUyMGZpbmUlMjBkaW5pbmd8ZW58MXx8fHwxNzczNTg1MTUwfDA&ixlib=rb-4.1.0&q=80&w=1080" },
  ];

  const handleSelect = (field: keyof FormData, value: string) => {
    setFormData({ ...formData, [field]: value });
    if (currentStep < steps.length - 1) {
      setTimeout(() => setCurrentStep(currentStep + 1), 300);
    }
  };

  const handleInputChange = (field: keyof FormData, value: string) => {
    setFormData({ ...formData, [field]: value });
  };

  const handleSubmitForm = () => {
    if (formData.destination && formData.travelers) {
      onSubmit(formData);
    }
  };

  return (
    <section className="min-h-screen pt-[120px] pb-24 px-8 relative overflow-hidden">
      {/* Background ambient lights */}
      <div className="absolute top-1/4 left-10 h-96 w-96 rounded-full bg-[#00F0FF]/10 blur-[150px]" />
      <div className="absolute bottom-1/4 right-10 h-96 w-96 rounded-full bg-[#8A2BE2]/10 blur-[150px]" />

      <div className="max-w-7xl mx-auto">
        {/* Header */}
        <motion.div
          initial={{ y: 20, opacity: 0 }}
          whileInView={{ y: 0, opacity: 1 }}
          viewport={{ once: true }}
          className="text-center mb-20"
        >
          <h2 
            className="text-6xl md:text-7xl font-black mb-6 bg-gradient-to-r from-white to-white/60 bg-clip-text text-transparent"
            style={{ fontFamily: "'Archivo Black', sans-serif" }}
          >
            CRAFT YOUR JOURNEY
          </h2>
          <p className="text-xl text-white/60" style={{ fontFamily: "'Inter', sans-serif" }}>
            Answer a few questions and let our AI agents create your perfect itinerary
          </p>
        </motion.div>

        {/* Progress Indicator */}
        <div className="flex justify-center gap-3 mb-16">
          {steps.map((step, index) => (
            <motion.div
              key={step.id}
              initial={{ scale: 0 }}
              animate={{ scale: 1 }}
              transition={{ delay: index * 0.1 }}
              className={`h-2 rounded-full transition-all duration-500 ${
                index <= currentStep 
                  ? "w-16 bg-gradient-to-r from-[#00F0FF] to-[#8A2BE2]" 
                  : "w-8 bg-white/10"
              }`}
            />
          ))}
        </div>

        {/* Form Container - Glassmorphism */}
        <motion.div
          layout
          className="backdrop-blur-xl bg-white/5 border border-white/10 rounded-[32px] p-12 shadow-[0_8px_32px_rgba(0,0,0,0.4)]"
        >
          <motion.div
            key={currentStep}
            initial={{ x: 100, opacity: 0 }}
            animate={{ x: 0, opacity: 1 }}
            exit={{ x: -100, opacity: 0 }}
            transition={{ duration: 0.5 }}
          >
            <h3 
              className="text-3xl font-bold text-white mb-8"
              style={{ fontFamily: "'Space Grotesk', sans-serif" }}
            >
              {steps[currentStep].title}
            </h3>

            {/* Budget Selection */}
            {currentStep === 0 && (
              <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
                {budgetOptions.map((option) => (
                  <motion.button
                    key={option.id}
                    whileHover={{ scale: 1.03, y: -4 }}
                    whileTap={{ scale: 0.98 }}
                    onClick={() => handleSelect("budget", option.id)}
                    className={`group relative p-8 rounded-[24px] border transition-all duration-300 ${
                      formData.budget === option.id
                        ? "bg-white/10 border-white/30 shadow-[0_0_30px_rgba(255,255,255,0.1)]"
                        : "bg-white/5 border-white/10 hover:border-white/20"
                    }`}
                  >
                    <div className={`h-16 w-16 rounded-2xl bg-gradient-to-br ${option.gradient} flex items-center justify-center mb-6 shadow-lg`}>
                      <option.icon className="h-8 w-8 text-white" />
                    </div>
                    <h4 className="text-2xl font-bold text-white mb-2" style={{ fontFamily: "'Space Grotesk', sans-serif" }}>
                      {option.label}
                    </h4>
                    <p className="text-white/60" style={{ fontFamily: "'Inter', sans-serif" }}>
                      {option.desc}
                    </p>
                  </motion.button>
                ))}
              </div>
            )}

            {/* Lifestyle Selection */}
            {currentStep === 1 && (
              <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
                {lifestyleOptions.map((option) => (
                  <motion.button
                    key={option.id}
                    whileHover={{ scale: 1.03, y: -4 }}
                    whileTap={{ scale: 0.98 }}
                    onClick={() => handleSelect("lifestyle", option.id)}
                    className={`group relative p-8 rounded-[24px] border transition-all duration-300 ${
                      formData.lifestyle === option.id
                        ? "bg-white/10 border-white/30 shadow-[0_0_30px_rgba(255,255,255,0.1)]"
                        : "bg-white/5 border-white/10 hover:border-white/20"
                    }`}
                  >
                    <div className={`h-16 w-16 rounded-2xl bg-gradient-to-br ${option.gradient} flex items-center justify-center mb-6 shadow-lg`}>
                      <option.icon className="h-8 w-8 text-white" />
                    </div>
                    <h4 className="text-2xl font-bold text-white mb-2" style={{ fontFamily: "'Space Grotesk', sans-serif" }}>
                      {option.label}
                    </h4>
                    <p className="text-white/60" style={{ fontFamily: "'Inter', sans-serif" }}>
                      {option.desc}
                    </p>
                  </motion.button>
                ))}
              </div>
            )}

            {/* Vacation Type Selection */}
            {currentStep === 2 && (
              <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
                {vacationTypeOptions.map((option) => (
                  <motion.button
                    key={option.id}
                    whileHover={{ scale: 1.03, y: -4 }}
                    whileTap={{ scale: 0.98 }}
                    onClick={() => handleSelect("vacationType", option.id)}
                    className={`group relative overflow-hidden h-80 rounded-[24px] border transition-all duration-300 ${
                      formData.vacationType === option.id
                        ? "border-white/30 shadow-[0_0_30px_rgba(255,255,255,0.1)]"
                        : "border-white/10 hover:border-white/20"
                    }`}
                  >
                    <Image 
                      src={option.image} 
                      alt={option.label}
                      fill
                      sizes="(max-width: 768px) 100vw, 33vw"
                      className="object-cover"
                    />
                    <div className="absolute inset-0 bg-gradient-to-t from-black via-black/60 to-transparent" />
                    <div className="absolute bottom-0 left-0 right-0 p-6">
                      <div className="flex items-center gap-3 mb-2">
                        <div className="h-12 w-12 rounded-xl bg-white/10 backdrop-blur-sm flex items-center justify-center border border-white/20">
                          <option.icon className="h-6 w-6 text-white" />
                        </div>
                        <h4 className="text-2xl font-bold text-white" style={{ fontFamily: "'Space Grotesk', sans-serif" }}>
                          {option.label}
                        </h4>
                      </div>
                      <p className="text-white/80" style={{ fontFamily: "'Inter', sans-serif" }}>
                        {option.desc}
                      </p>
                    </div>
                  </motion.button>
                ))}
              </div>
            )}

            {/* Destination Input */}
            {currentStep === 3 && (
              <div className="max-w-2xl mx-auto">
                <div className="relative">
                  <MapPin className="absolute left-6 top-1/2 -translate-y-1/2 h-6 w-6 text-[#00F0FF]" />
                  <input
                    type="text"
                    value={formData.destination}
                    onChange={(e) => handleInputChange("destination", e.target.value)}
                    onKeyDown={(e) => {
                      if (e.key === 'Enter' && formData.destination.trim()) {
                        setCurrentStep(4);
                      }
                    }}
                    placeholder="Where do you want to go?"
                    className="w-full bg-white/5 border border-white/10 rounded-[20px] pl-16 pr-6 py-6 text-white text-xl placeholder:text-white/40 focus:outline-none focus:border-[#00F0FF]/50 focus:shadow-[0_0_30px_rgba(0,240,255,0.2)] transition-all"
                    style={{ fontFamily: "'Inter', sans-serif" }}
                    autoFocus
                  />
                </div>

                <motion.div 
                  initial={{ opacity: 0, y: 10 }}
                  animate={{ opacity: 1, y: 0 }}
                  className="mt-8 flex justify-end"
                >
                  <motion.button
                    whileHover={{ scale: 1.05 }}
                    whileTap={{ scale: 0.95 }}
                    disabled={!formData.destination.trim()}
                    onClick={() => setCurrentStep(4)}
                    className="px-8 py-4 rounded-full bg-[#00F0FF]/10 text-[#00F0FF] border border-[#00F0FF]/30 font-medium flex items-center gap-2 hover:bg-[#00F0FF]/20 transition-all shadow-[0_0_20px_rgba(0,240,255,0.2)] disabled:opacity-50 disabled:cursor-not-allowed"
                  >
                    Continue
                    <ArrowRight className="h-5 w-5" />
                  </motion.button>
                </motion.div>
              </div>
            )}

            {/* Travelers Input */}
            {currentStep === 4 && (
              <div className="max-w-2xl mx-auto space-y-8">
                <div className="relative">
                  <Users className="absolute left-6 top-1/2 -translate-y-1/2 h-6 w-6 text-[#8A2BE2]" />
                  <input
                    type="number"
                    value={formData.travelers}
                    onChange={(e) => handleInputChange("travelers", e.target.value)}
                    onKeyDown={(e) => {
                      if (e.key === 'Enter' && formData.travelers) {
                        handleSubmitForm();
                      }
                    }}
                    placeholder="Number of travelers"
                    min="1"
                    className="w-full bg-white/5 border border-white/10 rounded-[20px] pl-16 pr-6 py-6 text-white text-xl placeholder:text-white/40 focus:outline-none focus:border-[#8A2BE2]/50 focus:shadow-[0_0_30px_rgba(138,43,226,0.2)] transition-all"
                    style={{ fontFamily: "'Inter', sans-serif" }}
                    autoFocus
                  />
                </div>

                <motion.button
                  whileHover={{ scale: 1.02 }}
                  whileTap={{ scale: 0.98 }}
                  onClick={handleSubmitForm}
                  disabled={!formData.destination || !formData.travelers}
                  className="w-full py-6 rounded-[20px] bg-gradient-to-r from-[#00F0FF] to-[#8A2BE2] text-white text-xl font-bold flex items-center justify-center gap-3 shadow-[0_0_40px_rgba(0,240,255,0.3)] disabled:opacity-50 disabled:cursor-not-allowed"
                  style={{ fontFamily: "'Space Grotesk', sans-serif" }}
                >
                  Generate My Itinerary
                  <ArrowRight className="h-6 w-6" />
                </motion.button>
              </div>
            )}
          </motion.div>

          {/* Navigation */}
          {currentStep > 0 && currentStep <= 4 && (
            <motion.button
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              onClick={() => setCurrentStep(currentStep - 1)}
              className="mt-8 text-white/60 hover:text-white transition-colors flex items-center gap-2"
              style={{ fontFamily: "'Inter', sans-serif" }}
            >
              ← Back
            </motion.button>
          )}
        </motion.div>
      </div>
    </section>
  );
}
