"""奖励配置验证器

验证奖励配置的业务逻辑。
"""

from typing import Dict, Any, Tuple, List


def validate_field(field_name: str, value: Any, params: Dict[str, Any], row_data: Dict[str, Any]) -> Tuple[bool, str]:
    """验证奖励配置字段
    
    验证规则：
    1. 必须是列表类型
    2. 每个奖励必须有有效的ItemID、Count和Probability
    3. 概率值必须在0-1之间
    4. 数量必须大于0
    """
    
    # 检查是否为空
    if value is None:
        return False, f"Field '{field_name}' is required"
    
    # 检查是否为列表
    if not isinstance(value, list):
        return False, f"Field '{field_name}' must be a list, got {type(value).__name__}"
    
    # 检查是否为空列表
    if len(value) == 0:
        return False, f"Field '{field_name}' cannot be empty, at least one reward is required"
    
    # 验证每个奖励项
    for i, reward in enumerate(value):
        if not isinstance(reward, dict):
            return False, f"Field '{field_name}' item {i+1} must be an object, got {type(reward).__name__}"
        
        # 验证必需字段
        if 'ItemID' not in reward:
            return False, f"Field '{field_name}' item {i+1} missing required field 'ItemID'"
        
        if 'Count' not in reward:
            return False, f"Field '{field_name}' item {i+1} missing required field 'Count'"
        
        # 验证ItemID
        try:
            item_id = int(reward['ItemID'])
            if item_id <= 0:
                return False, f"Field '{field_name}' item {i+1}: ItemID must be positive, got {item_id}"
        except (ValueError, TypeError):
            return False, f"Field '{field_name}' item {i+1}: ItemID must be an integer, got '{reward['ItemID']}'"
        
        # 验证Count
        try:
            count = int(reward['Count'])
            if count <= 0:
                return False, f"Field '{field_name}' item {i+1}: Count must be positive, got {count}"
        except (ValueError, TypeError):
            return False, f"Field '{field_name}' item {i+1}: Count must be an integer, got '{reward['Count']}'"
        
        # 验证Probability（可选字段）
        if 'Probability' in reward:
            try:
                probability = float(reward['Probability'])
                if probability < 0 or probability > 1:
                    return False, f"Field '{field_name}' item {i+1}: Probability must be between 0-1, got {probability}"
            except (ValueError, TypeError):
                return False, f"Field '{field_name}' item {i+1}: Probability must be a number, got '{reward['Probability']}'"
    
    # 业务逻辑验证
    return _validate_business_rules(field_name, value, params, row_data)


def _validate_business_rules(field_name: str, rewards: List[Dict[str, Any]], params: Dict[str, Any], row_data: Dict[str, Any]) -> Tuple[bool, str]:
    """验证业务规则"""
    
    # 检查奖励数量限制
    max_rewards = params.get('max_rewards', 5)
    if len(rewards) > max_rewards:
        return False, f"Field '{field_name}': Too many rewards (max {max_rewards}), got {len(rewards)}"
    
    # 检查是否有重复的ItemID
    item_ids = []
    for reward in rewards:
        item_id = reward['ItemID']
        if item_id in item_ids:
            return False, f"Field '{field_name}': Duplicate ItemID {item_id} found"
        item_ids.append(item_id)
    
    # 检查概率总和（如果所有奖励都有概率）
    probabilities = [reward.get('Probability') for reward in rewards if 'Probability' in reward]
    if len(probabilities) == len(rewards):  # 所有奖励都有概率
        total_probability = sum(probabilities)
        if total_probability > 1.0:
            return False, f"Field '{field_name}': Total probability {total_probability} exceeds 1.0"
    
    # 根据成就类型验证奖励合理性
    achievement_type = row_data.get('AchievementType', '')
    if achievement_type == 'daily':
        for reward in rewards:
            if reward['Count'] > 100:
                return False, f"Field '{field_name}': Daily achievement reward count too high ({reward['Count']}), max 100"
    elif achievement_type == 'event':
        pass
    
    return True, ""


def validate_row(row_data: Dict[str, Any], export_config: Dict[str, Any]) -> Tuple[bool, str]:
    """行级验证：检查成就类型和奖励配置的匹配性"""
    achievement_type = row_data.get('AchievementType', '')
    reward_config = row_data.get('RewardConfig', [])
    
    if achievement_type == 'main' and len(reward_config) < 2:
        return False, "Main achievements should have at least 2 rewards"
    
    if achievement_type == 'daily' and len(reward_config) > 3:
        return False, "Daily achievements should not have more than 3 rewards"
    
    return True, ""