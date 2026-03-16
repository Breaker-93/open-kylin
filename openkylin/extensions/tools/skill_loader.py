"""OpenClaw Skill 加载器 - OpenClaw Skill Loader

支持加载 OpenClaw SKILL.md 格式的技能。
"""

import json
import os
import platform
import re
import shutil
import subprocess
import sys
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

import yaml

from openkylin.core.plugin import PluginMetadata, PluginType
from openkylin.extensions.tools.base import Tool, ToolResult


@dataclass
class SkillMetadata:
    """Skill 元数据"""
    name: str
    description: str
    version: str = "1.0.0"
    homepage: str = ""
    user_invocable: bool = True
    disable_model_invocation: bool = False
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass
class Skill:
    """Skill 对象"""
    metadata: SkillMetadata
    directory: Path
    instructions: str = ""
    loaded: bool = False

    @property
    def dependencies(self) -> dict[str, Any]:
        """获取依赖要求"""
        return self.metadata.metadata.get("openclaw", {}).get("requires", {})


class SkillLoader:
    """OpenClaw Skill 加载器

    支持从目录加载 SKILL.md 格式的技能。

    目录结构:
        skill-folder/
        ├── SKILL.md              # 必需
        ├── scripts/              # 可执行脚本
        ├── references/           # 参考文档
        └── assets/               # 资源文件
    """

    def __init__(self, skills_dir: Path | None = None):
        self._skills_dir = skills_dir or Path.home() / ".openkylin" / "skills"
        self._skills: dict[str, Skill] = {}
        self._search_paths: list[Path] = []

    @property
    def skills_dir(self) -> Path:
        return self._skills_dir

    def add_search_path(self, path: Path) -> None:
        """添加搜索路径"""
        if path.exists() and path.is_dir():
            self._search_paths.append(path)

    def discover(self) -> list[str]:
        """发现并加载所有 Skill

        Returns:
            加载的 Skill 名称列表
        """
        discovered = []

        # 搜索所有路径
        all_paths = [self._skills_dir] + self._search_paths
        for search_path in all_paths:
            if not search_path.exists():
                continue

            for item in search_path.iterdir():
                if item.is_dir() and (item / "SKILL.md").exists():
                    try:
                        skill = self._load_skill(item)
                        self._skills[skill.metadata.name] = skill
                        discovered.append(skill.metadata.name)
                    except Exception as e:
                        print(f"Failed to load skill '{item.name}': {e}")

        return discovered

    def _load_skill(self, directory: Path) -> Skill:
        """加载单个 Skill"""
        skill_file = directory / "SKILL.md"
        content = skill_file.read_text(encoding="utf-8")

        # 解析 YAML Frontmatter
        metadata, instructions = self._parse_skill_md(content)

        return Skill(
            metadata=metadata,
            directory=directory,
            instructions=instructions,
            loaded=True,
        )

    def _parse_skill_md(self, content: str) -> tuple[SkillMetadata, str]:
        """解析 SKILL.md 内容"""
        # 提取 Frontmatter
        pattern = r"^---\n(.*?)\n---\n(.*)$"
        match = re.match(pattern, content, re.DOTALL)

        if not match:
            # 没有 Frontmatter，使用整个文件作为指令
            return SkillMetadata(
                name="unknown",
                description=content[:100]
            ), content

        frontmatter_text = match.group(1)
        instructions = match.group(2)

        # 解析 YAML
        try:
            data = yaml.safe_load(frontmatter_text)
        except yaml.YAMLError:
            data = {}

        metadata = SkillMetadata(
            name=data.get("name", "unknown"),
            description=data.get("description", ""),
            version=data.get("version", "1.0.0"),
            homepage=data.get("homepage", ""),
            user_invocable=data.get("user-invocable", True),
            disable_model_invocation=data.get("disable-model-invocation", False),
            metadata=json.loads(data.get("metadata", "{}")) if isinstance(data.get("metadata"), str) else data.get("metadata", {}),
        )

        return metadata, instructions.strip()

    def get(self, name: str) -> Skill | None:
        """获取 Skill"""
        return self._skills.get(name)

    def list(self) -> list[str]:
        """列出所有 Skill"""
        return list(self._skills.keys())

    def check_dependencies(self, name: str) -> tuple[bool, list[str]]:
        """检查 Skill 依赖是否满足

        Returns:
            (是否满足, 缺失列表)
        """
        skill = self._skills.get(name)
        if not skill:
            return False, [f"Skill '{name}' not found"]

        deps = skill.dependencies
        missing = []

        # 检查命令行工具
        for bin in deps.get("bins", []):
            if shutil.which(bin) is None:
                missing.append(f"Binary: {bin}")

        # 检查环境变量
        for env in deps.get("env", []):
            if env not in os.environ:
                missing.append(f"Env: {env}")

        # 检查平台
        required_os = deps.get("os")
        if required_os and platform.system().lower() != required_os.lower():
            missing.append(f"OS: {required_os}")

        return len(missing) == 0, missing

    async def execute_script(self, skill_name: str, script_name: str, args: dict[str, Any] | None = None) -> ToolResult:
        """执行 Skill 脚本

        Args:
            skill_name: Skill 名称
            script_name: 脚本文件名
            args: 脚本参数

        Returns:
            执行结果
        """
        skill = self._skills.get(skill_name)
        if not skill:
            return ToolResult(success=False, error=f"Skill '{skill_name}' not found")

        script_path = skill.directory / "scripts" / script_name
        if not script_path.exists():
            return ToolResult(success=False, error=f"Script '{script_name}' not found")

        # 检查执行权限
        if not os.access(script_path, os.X_OK):
            # 尝试添加执行权限
            try:
                os.chmod(script_path, 0o755)
            except Exception:
                pass

        try:
            env = os.environ.copy()
            if args:
                env.update(args)

            # 执行脚本
            result = subprocess.run(
                [str(script_path)],
                capture_output=True,
                text=True,
                env=env,
                cwd=str(skill.directory),
            )

            if result.returncode == 0:
                return ToolResult(
                    success=True,
                    result=result.stdout,
                    metadata={"returncode": result.returncode}
                )
            else:
                return ToolResult(
                    success=False,
                    error=result.stderr,
                    metadata={"returncode": result.returncode}
                )

        except Exception as e:
            return ToolResult(success=False, error=str(e))

    def get_instructions(self, name: str) -> str:
        """获取 Skill 指令"""
        skill = self._skills.get(name)
        if not skill:
            return ""
        return skill.instructions

    def to_tool(self, skill: Skill) -> "SkillTool":
        """将 Skill 转换为 Tool"""
        return SkillTool(skill)


class SkillTool(Tool):
    """Skill 工具包装器

    将加载的 Skill 包装为可执行的 Tool
    """

    def __init__(self, skill: Skill):
        super().__init__()
        self._skill = skill
        self._definition = None

    @property
    def metadata(self) -> PluginMetadata:
        return PluginMetadata(
            name=self._skill.metadata.name,
            plugin_type=PluginType.TOOL,
            description=self._skill.metadata.description,
        )

    @property
    def name(self) -> str:
        return self._skill.metadata.name

    @property
    def description(self) -> str:
        return self._skill.metadata.description

    @property
    def instructions(self) -> str:
        return self._skill.instructions

    def get_parameters(self) -> dict[str, Any]:
        """获取参数定义"""
        deps = self._skill.dependencies
        params = {
            "type": "object",
            "properties": {},
            "required": [],
        }

        # 从 metadata 中提取参数信息（如果有）
        tool_params = self._skill.metadata.metadata.get("toolParams", {})
        if tool_params:
            params["properties"] = tool_params

        return params

    async def execute(self, **kwargs) -> ToolResult:
        """执行 Skill"""
        # 检查依赖
        loader = SkillLoader()  # 这里应该传入实际的 loader 实例
        satisfied, missing = loader.check_dependencies(self.name)
        if not satisfied:
            return ToolResult(
                success=False,
                error=f"Missing dependencies: {', '.join(missing)}"
            )

        # 返回 Skill 指令供 Agent 使用
        return ToolResult(
            success=True,
            result=self.instructions,
            metadata={"type": "instructions"}
        )


# Skill 存储路径配置
DEFAULT_SKILL_PATHS = [
    Path.cwd() / "skills",           # 工作区
    Path.home() / ".openkylin" / "skills",  # 全局
]
