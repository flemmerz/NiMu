// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

interface ITokenH2O {
    event Staked(address indexed user, uint256 amount);
    event Unstaked(address indexed user, uint256 amount);
    event RewardDistributed(address indexed user, uint256 amount);

    function stake(uint256 amount) external;
    function unstake() external;
    function getStakedBalance(address user) external view returns (uint256);
    function getStakingTimestamp(address user) external view returns (uint256);
    function distributeReward(address user, uint256 amount) external;
}