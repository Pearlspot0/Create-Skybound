package com.create_skybound.item;

import com.create_skybound.blockentity.MooringCleatBlockEntity;
import com.create_skybound.blockentity.MooringWinchBlockEntity;
import com.create_skybound.registry.ModSounds;
import net.minecraft.core.BlockPos;
import net.minecraft.network.chat.Component;
import net.minecraft.sounds.SoundSource;
import net.minecraft.world.InteractionHand;
import net.minecraft.world.InteractionResult;
import net.minecraft.world.InteractionResultHolder;
import net.minecraft.world.entity.player.Player;
import net.minecraft.world.item.Item;
import net.minecraft.world.item.ItemStack;
import net.minecraft.world.item.context.UseOnContext;
import net.minecraft.world.level.Level;
import net.minecraft.world.level.block.entity.BlockEntity;

import java.util.Map;
import java.util.UUID;
import java.util.concurrent.ConcurrentHashMap;

public class MooringCableItem extends Item {
    // Session anchor cache for linking players
    private static final Map<UUID, BlockPos> PENDING_ANCHORS = new ConcurrentHashMap<>();

    public MooringCableItem(Properties properties) {
        super(properties);
    }

    @Override
    public InteractionResult useOn(UseOnContext context) {
        Level level = context.getLevel();
        BlockPos clickedPos = context.getClickedPos();
        Player player = context.getPlayer();
        if (player == null) return InteractionResult.PASS;

        BlockEntity be = level.getBlockEntity(clickedPos);
        boolean isCleat = be instanceof MooringCleatBlockEntity;
        boolean isWinch = be instanceof MooringWinchBlockEntity;

        if (!isCleat && !isWinch) {
            return InteractionResult.PASS;
        }

        if (level.isClientSide) {
            return InteractionResult.SUCCESS;
        }

        UUID uuid = player.getUUID();
        BlockPos firstPos = PENDING_ANCHORS.get(uuid);

        if (firstPos == null) {
            PENDING_ANCHORS.put(uuid, clickedPos);
            level.playSound(null, clickedPos, ModSounds.CLAMP_LOCK.get(), SoundSource.PLAYERS, 0.8f, 1.2f);
            player.displayClientMessage(Component.translatable("message.create_skybound.cable_first_anchor",
                    clickedPos.getX(), clickedPos.getY(), clickedPos.getZ()), true);
            return InteractionResult.SUCCESS;
        }

        if (firstPos.equals(clickedPos)) {
            PENDING_ANCHORS.remove(uuid);
            player.displayClientMessage(Component.translatable("message.create_skybound.cable_cleared"), true);
            return InteractionResult.SUCCESS;
        }

        double distSq = firstPos.distSqr(clickedPos);
        if (distSq > 48 * 48) {
            player.displayClientMessage(Component.translatable("message.create_skybound.cable_too_far"), true);
            return InteractionResult.FAIL;
        }

        BlockEntity firstBe = level.getBlockEntity(firstPos);
        if (firstBe == null) {
            PENDING_ANCHORS.remove(uuid);
            player.displayClientMessage(Component.translatable("message.create_skybound.cable_first_lost"), true);
            return InteractionResult.FAIL;
        }

        // Connect the two ends
        if (firstBe instanceof MooringCleatBlockEntity cleat1) {
            cleat1.setLinkedPos(clickedPos);
        } else if (firstBe instanceof MooringWinchBlockEntity winch1) {
            winch1.setLinkedPos(clickedPos);
        }

        if (be instanceof MooringCleatBlockEntity cleat2) {
            cleat2.setLinkedPos(firstPos);
        } else if (be instanceof MooringWinchBlockEntity winch2) {
            winch2.setLinkedPos(firstPos);
        }

        PENDING_ANCHORS.remove(uuid);
        if (!player.getAbilities().instabuild) {
            context.getItemInHand().shrink(1);
        }

        level.playSound(null, clickedPos, ModSounds.CLAMP_LOCK.get(), SoundSource.BLOCKS, 1.0f, 1.0f);
        player.displayClientMessage(Component.translatable("message.create_skybound.cable_connected"), true);
        return InteractionResult.SUCCESS;
    }

    @Override
    public InteractionResultHolder<ItemStack> use(Level level, Player player, InteractionHand hand) {
        if (player.isShiftKeyDown()) {
            if (!level.isClientSide) {
                PENDING_ANCHORS.remove(player.getUUID());
                player.displayClientMessage(Component.translatable("message.create_skybound.cable_cleared"), true);
            }
            return InteractionResultHolder.sidedSuccess(player.getItemInHand(hand), level.isClientSide);
        }
        return super.use(level, player, hand);
    }
}
