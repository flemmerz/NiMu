const hre = require("hardhat");

async function main() {
  // Deploy TokenH2O
  const TokenH2O = await hre.ethers.getContractFactory("TokenH2O");
  const tokenH2O = await TokenH2O.deploy();
  await tokenH2O.deployed();
  console.log("TokenH2O deployed to:", tokenH2O.address);

  // Deploy TokenMu
  const TokenMu = await hre.ethers.getContractFactory("TokenMu");
  const tokenMu = await TokenMu.deploy();
  await tokenMu.deployed();
  console.log("TokenMu deployed to:", tokenMu.address);

  // Deploy InsuranceCell
  const InsuranceCell = await hre.ethers.getContractFactory("InsuranceCell");
  const insuranceCell = await InsuranceCell.deploy(tokenMu.address, 8000); // 80% target loss ratio
  await insuranceCell.deployed();
  console.log("InsuranceCell deployed to:", insuranceCell.address);
}

main()
  .then(() => process.exit(0))
  .catch((error) => {
    console.error(error);
    process.exit(1);
  });