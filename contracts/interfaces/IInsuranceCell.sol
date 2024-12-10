// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

interface IInsuranceCell {
    struct Policy {
        uint256 premium;
        uint256 coverage;
        uint256 startTime;
        uint256 endTime;
        bool active;
    }

    event PolicyPurchased(
        address indexed member,
        uint256 premium,
        uint256 coverage,
        uint256 duration
    );

    event ClaimSubmitted(
        address indexed member,
        uint256 amount,
        string reason
    );

    event ClaimProcessed(
        address indexed member,
        uint256 claimId,
        bool approved,
        uint256 amount
    );

    function purchasePolicy(uint256 premium, uint256 coverage, uint256 duration) external;
    function submitClaim(uint256 amount, string calldata reason) external;
    function processClaim(uint256 claimId, bool approved, uint256 amount) external;
    function getPolicy(address member) external view returns (Policy memory);
    function getLossRatio() external view returns (uint256);
    function getTotalPremiums() external view returns (uint256);
    function getTotalClaims() external view returns (uint256);
}