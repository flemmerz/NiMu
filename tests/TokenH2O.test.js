const { expect } = require("chai");
const { ethers } = require("hardhat");

describe("TokenH2O", function () {
  let TokenH2O;
  let tokenH2O;
  let owner;
  let addr1;
  let addr2;

  beforeEach(async function () {
    TokenH2O = await ethers.getContractFactory("TokenH2O");
    [owner, addr1, addr2] = await ethers.getSigners();
    tokenH2O = await TokenH2O.deploy();
  });

  describe("Deployment", function () {
    it("Should set the right owner", async function () {
      expect(await tokenH2O.owner()).to.equal(owner.address);
    });

    it("Should assign the total supply of tokens to the owner", async function () {
      const ownerBalance = await tokenH2O.balanceOf(owner.address);
      expect(await tokenH2O.totalSupply()).to.equal(ownerBalance);
    });
  });

  describe("Staking", function () {
    it("Should allow users to stake tokens", async function () {
      const stakeAmount = ethers.utils.parseEther("100");
      await tokenH2O.transfer(addr1.address, stakeAmount);
      await tokenH2O.connect(addr1).approve(tokenH2O.address, stakeAmount);
      await tokenH2O.connect(addr1).stake(stakeAmount);
      expect(await tokenH2O.getStakedBalance(addr1.address)).to.equal(stakeAmount);
    });
  });
});