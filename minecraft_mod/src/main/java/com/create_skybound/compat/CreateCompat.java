package com.create_skybound.compat;

import net.minecraft.core.Direction;
import net.minecraft.core.registries.Registries;
import net.minecraft.resources.ResourceLocation;
import net.minecraft.tags.TagKey;
import net.minecraft.world.entity.player.Player;
import net.minecraft.world.item.Item;
import net.minecraft.world.item.ItemStack;
import net.minecraft.world.level.block.state.BlockState;
import net.minecraft.world.level.block.state.properties.BlockStateProperties;

public class CreateCompat {
    public static final TagKey<Item> COMMON_WRENCH_TAG =
            TagKey.create(Registries.ITEM, ResourceLocation.fromNamespaceAndPath("c", "tools/wrench"));

    public static boolean isWrench(ItemStack stack) {
        if (stack.isEmpty()) return false;
        if (stack.is(COMMON_WRENCH_TAG)) return true;
        String name = stack.getItem().toString().toLowerCase();
        return name.contains("wrench");
    }

    public static BlockState rotateBlock(BlockState state) {
        if (state.hasProperty(BlockStateProperties.HORIZONTAL_FACING)) {
            Direction current = state.getValue(BlockStateProperties.HORIZONTAL_FACING);
            return state.setValue(BlockStateProperties.HORIZONTAL_FACING, current.getClockWise());
        }
        if (state.hasProperty(BlockStateProperties.FACING)) {
            Direction current = state.getValue(BlockStateProperties.FACING);
            Direction[] values = Direction.values();
            int nextIdx = (current.ordinal() + 1) % values.length;
            return state.setValue(BlockStateProperties.FACING, values[nextIdx]);
        }
        return state;
    }
}
