package com.create_skybound.block;

import com.create_skybound.registry.ModBlocks;
import com.create_skybound.registry.ModSounds;
import net.minecraft.core.BlockPos;
import net.minecraft.core.Direction;
import net.minecraft.core.particles.ParticleTypes;
import net.minecraft.sounds.SoundSource;
import net.minecraft.world.InteractionHand;
import net.minecraft.world.ItemInteractionResult;
import net.minecraft.world.entity.player.Player;
import net.minecraft.world.item.ItemStack;
import net.minecraft.world.item.context.BlockPlaceContext;
import net.minecraft.world.level.BlockGetter;
import net.minecraft.world.level.Level;
import net.minecraft.world.level.block.Block;
import net.minecraft.world.level.block.Blocks;
import net.minecraft.world.level.block.RenderShape;
import net.minecraft.world.level.block.state.BlockState;
import net.minecraft.world.level.block.state.StateDefinition;
import net.minecraft.world.level.block.state.properties.BlockStateProperties;
import net.minecraft.world.level.block.state.properties.BooleanProperty;
import net.minecraft.world.level.block.state.properties.DirectionProperty;
import net.minecraft.world.phys.BlockHitResult;
import net.minecraft.world.phys.Vec3;
import net.minecraft.world.phys.shapes.CollisionContext;
import net.minecraft.world.phys.shapes.VoxelShape;
import org.jetbrains.annotations.Nullable;

public class DockingGangwayBlock extends Block {
    public static final DirectionProperty FACING = BlockStateProperties.HORIZONTAL_FACING;
    public static final BooleanProperty EXTENDED = BooleanProperty.create("extended");
    public static final BooleanProperty POWERED = BlockStateProperties.POWERED;

    private static final VoxelShape BASE_SHAPE = Block.box(0.0, 10.0, 0.0, 16.0, 16.0, 16.0);

    public DockingGangwayBlock(Properties properties) {
        super(properties);
        this.registerDefaultState(this.stateDefinition.any()
                .setValue(FACING, Direction.NORTH)
                .setValue(EXTENDED, false)
                .setValue(POWERED, false));
    }

    @Override
    protected void createBlockStateDefinition(StateDefinition.Builder<Block, BlockState> builder) {
        builder.add(FACING, EXTENDED, POWERED);
    }

    @Nullable
    @Override
    public BlockState getStateForPlacement(BlockPlaceContext context) {
        Direction dir = context.getHorizontalDirection().getOpposite();
        boolean powered = context.getLevel().hasNeighborSignal(context.getClickedPos());
        return this.defaultBlockState()
                .setValue(FACING, dir)
                .setValue(POWERED, powered)
                .setValue(EXTENDED, false);
    }

    @Override
    protected VoxelShape getShape(BlockState state, BlockGetter level, BlockPos pos, CollisionContext context) {
        return BASE_SHAPE;
    }

    @Override
    protected RenderShape getRenderShape(BlockState state) {
        return RenderShape.MODEL;
    }

    @Override
    protected void neighborChanged(BlockState state, Level level, BlockPos pos, Block neighborBlock, BlockPos neighborPos, boolean movedByPiston) {
        if (!level.isClientSide) {
            boolean isPowered = level.hasNeighborSignal(pos);
            if (isPowered != state.getValue(POWERED)) {
                setExtendedState(level, pos, state, isPowered, isPowered);
            }
        }
    }

    @Override
    protected ItemInteractionResult useItemOn(ItemStack stack, BlockState state, Level level, BlockPos pos, Player player, InteractionHand hand, BlockHitResult hitResult) {
        if (!level.isClientSide) {
            boolean next = !state.getValue(EXTENDED);
            setExtendedState(level, pos, state, next, state.getValue(POWERED));
        }
        return ItemInteractionResult.SUCCESS;
    }

    public void setExtendedState(Level level, BlockPos pos, BlockState state, boolean extended, boolean powered) {
        level.setBlock(pos, state.setValue(EXTENDED, extended).setValue(POWERED, powered), 3);
        level.playSound(null, pos, ModSounds.GANGWAY_EXTEND.get(), SoundSource.BLOCKS, 1.0f, extended ? 1.0f : 0.8f);

        Direction facing = state.getValue(FACING);
        for (int i = 1; i <= 2; i++) {
            BlockPos targetPos = pos.relative(facing, i);
            if (extended) {
                if (level.getBlockState(targetPos).isAir()) {
                    level.setBlock(targetPos, ModBlocks.DOCKING_GANGWAY_SEGMENT.get().defaultBlockState().setValue(FACING, facing), 3);
                }
            } else {
                BlockState targetState = level.getBlockState(targetPos);
                if (targetState.is(ModBlocks.DOCKING_GANGWAY_SEGMENT.get())) {
                    level.setBlock(targetPos, Blocks.AIR.defaultBlockState(), 3);
                }
            }
        }
    }

    @Override
    protected void onRemove(BlockState state, Level level, BlockPos pos, BlockState newState, boolean isMoving) {
        if (!state.is(newState.getBlock()) && state.getValue(EXTENDED)) {
            Direction facing = state.getValue(FACING);
            for (int i = 1; i <= 2; i++) {
                BlockPos targetPos = pos.relative(facing, i);
                if (level.getBlockState(targetPos).is(ModBlocks.DOCKING_GANGWAY_SEGMENT.get())) {
                    level.setBlock(targetPos, Blocks.AIR.defaultBlockState(), 3);
                }
            }
        }
        super.onRemove(state, level, pos, newState, isMoving);
    }
}
