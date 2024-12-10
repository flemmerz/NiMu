# NiMu - Decentralized Trade Credit Insurance Protocol

NiMu is a blockchain-based mutual insurance protocol specifically designed for trade credit insurance. It leverages real-time payment data and smart contracts to provide dynamic, transparent, and efficient credit risk protection for businesses.

## Overview

NiMu implements a "Pay-As-You-Trade" model where members only pay for the actual credit they extend. Key features include:

- Decentralized mutual insurance structure
- Real-time payment data integration
- Dynamic premium pricing based on risk assessment
- Dual token system (H2O utility token and Mu security token)
- Smart contract-based claims processing
- Member governance system

## Repository Structure

```
/NiMu
├── /contracts         # Smart contracts written in Solidity
├── /backend           # Node.js backend for APIs and services
├── /frontend          # React.js-based frontend application
├── /docs              # Documentation for the project
├── /scripts           # Deployment scripts and automation tools
├── /tests             # Unit and integration test cases
├── .github            # GitHub-specific configurations
└── package.json       # Shared dependencies
```

## Getting Started

### Prerequisites

- Node.js >= 16
- Hardhat
- MongoDB
- MetaMask or similar Web3 wallet

### Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/flemmerz/NiMu.git
   cd NiMu
   ```

2. Install dependencies:
   ```bash
   npm install
   ```

3. Set up environment variables:
   ```bash
   cp .env.example .env
   ```

4. Run development environment:
   ```bash
   npm run dev
   ```

## Contributing

Please read [CONTRIBUTING.md](docs/CONTRIBUTING.md) for details on our code of conduct and the process for submitting pull requests.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.