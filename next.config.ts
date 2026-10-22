import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  // Le prévisualiseur sert l'application sous {port}-{sandbox}.e2b.app
  allowedDevOrigins: ["*.e2b.app", "*.arena.ai"],
  experimental: {
    // les appels aux API scientifiques partent du navigateur, pas du serveur
    serverActions: { allowedOrigins: ["*.e2b.app", "*.arena.ai"] },
  },
};

export default nextConfig;
